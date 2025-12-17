import json
import Data_loader
import Data_process
import Load_llm
import Decoupled_component

def general_line(
    compress_method,
    dataset,
    ratio,
    auto_para_label=2,
    compress_question=False,
    folder_path=""
):
    if dataset[0:5]=="GSM8K":
        prompt_path="prompt_"+dataset[5:]
        dataset="GSM8K"
    all_data=Data_loader.data_loader(dataset)
    ratio_list=ratio.split(",")
    if dataset=="GSM8K":
        GSM8K_prompt=open("dataset/gsm8k_prompt/"+prompt_path+".txt",'r').read()
        print("GSM8K_prompt",prompt_path)
    else:
        GSM8K_prompt=None
    model_path="Llama-2-7b-hf"
    (model,
     tokenizer,
     context_idxs,
     max_position_embeddings,
     device_map)\
        =(Load_llm.load_llm(model_path,False))

    if compress_method=="selecting":
        from selective_context.selective_context import SelectiveContext

        if dataset=="PeopleDaily":
            sc=SelectiveContext(model_type='llama2',lang='zh')
        else:
            sc=SelectiveContext(model_type='llama2')
    elif compress_method=="llmlingua":
        from llmingua.prompt_compressor import PromptCompressor
        llm_lingua=PromptCompressor(
            model_name="Llama-2-7b-hf",
            device_map="cuda",  # Device environment (e.g., 'cuda', 'cpu', 'mps')
            model_config={},  # Configuration for the Huggingface model
            open_api_config={},  # Configuration for OpenAI Embedding
        )
    elif compress_method=="longllmlingua":
        from llmlingua_new import PromptCompressor
        llm_lingua=PromptCompressor()
    elif compress_method=="llmlingua2":
        from llmlingua_new import PromptCompressor
        llm_lingua=PromptCompressor(
            model_name="llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,  # Whether to use llmlingua-2
        )
    elif compress_method=="Qwen2-72B-Instruct_local_vllm":
        from openai import OpenAI
        client=OpenAI(base_url="http://localhost:8000/v1",api_key="none")
        # pass
    elif compress_method=="original":
        pass
    else:
        import Qwen
        # load compresser
        if compress_method=="Qwen2-7B-Instruct_local":
            Qwen_model_path="Qwen/Qwen2-7B-Instruct"
            Qwen_model,Qwen_tokenizer=Qwen.Qwen_load(Qwen_model_path)
        elif compress_method=="Qwen2-72B-Instruct_local":
            Qwen_model_path="Qwen/Qwen2-72B-Instruct"
            Qwen_model,Qwen_tokenizer=Qwen.Qwen_load(Qwen_model_path)

    good=0
    bad=0
    all_revised_prompt_list=[]
    all_standard_answer=[]
    all_abstract=[]
    for dex,data in enumerate(all_data):
        # if dex>500 and dataset in ["hotpotQA","BBCnews","LongBench"]:
        if dex>500 and dataset in ["BBCnews"]:
            break
        if dex>100 and dataset in ["LongBench"]:
            break

        if dataset=="arXiv":
            (sentences_list,
             endlabels_list,
             question,
             abstract,
             sum_of_length,
             badlabel)=(
                Data_process.data_process_for_arXiv(
                    data,
                    dataset,
                    compress_question,
                    tokenizer,
                    sent_simplify_label=True,
                ))
        else:
            (sentences_list,
             endlabels_list,
             question,
             badlabel)\
                =Data_process.data_process(
                data,
                dataset,
                compress_question,
                # auto_para_label,
                GSM8K_prompt,
                tokenizer
            )
        bad+=badlabel
        good+=(1-badlabel)
        if badlabel==0:
            # or dataset=="arXiv":
            standard_prompt=""
            for sentence,endlabel in zip(sentences_list,endlabels_list):
                standard_prompt+=sentence
                for i in range(endlabel):
                    standard_prompt+="\n"

            if compress_method in ["llmlingua","longllmlingua"]:
                if not compress_question:
                    standard_prompt+=question
                context_list=[""]
                for sentence,endlabel in zip(sentences_list,endlabels_list):
                    context_list[-1]+=sentence
                    if endlabel>=auto_para_label:
                        context_list.append("")
                    else:
                        for i in range(endlabel):
                            context_list[-1]+="\n"
                if context_list[-1]=="":
                    context_list=context_list[:-2]
            revised_prompt_list=[]
            for ratio in ratio_list:
                ratio=float(ratio)
                if dataset in ["LongBench","RULER_niah"] and compress_method=="llmlingua2":
                    length=len(tokenizer.tokenize(standard_prompt))
                    ratio=(3000/length)*ratio
                    ratio=min(ratio,0.9999)

                Qwen_compress_prompt="Eliminate repetitive elements and present the text concisely, ensuring that key details and logical processes are retained.\n\n"


                if compress_method=="selecting":
                    context,reduced_content=sc(standard_prompt,reduce_ratio=1-ratio)
                    tmp_compress_prompt=context.replace("▁"," ")

                elif compress_method=="llmlingua":
                    compressed_prompt=llm_lingua.compress_prompt(
                        ratio=(1.0-ratio),
                        context=context_list,
                        question=question,
                    )
                    tmp_compress_prompt=compressed_prompt["compressed_prompt"]
                elif compress_method=="llmlingua2":

                    tmp_compress_prompt=llm_lingua.compress_prompt(standard_prompt,rate=ratio,force_tokens=['\n','?'])['compressed_prompt']
                    # print([tmp_compress_prompt])
                elif compress_method=="longllmlingua":
                    try:
                        tmp_compress_prompt=llm_lingua.compress_prompt(
                            context_list,
                            question=question,
                            rate=ratio,
                            # Set the special parameter for LongLLMLingua
                            condition_in_question="after_condition",
                            reorder_context="sort",
                            dynamic_context_compression_ratio=0.3,  # or 0.4
                            condition_compare=True,
                            context_budget="+100",
                            rank_method="longllmlingua",
                        )["compressed_prompt"]
                    except:
                        tmp_compress_prompt=""

                elif compress_method in ["Qwen2-7B-Instruct_local","Qwen2-72B-Instruct_local"]:
                    tmp_compress_prompt=Qwen.Qwen_generate_local(
                        model=Qwen_model,
                        tokenizer=Qwen_tokenizer,
                        prompt=Qwen_compress_prompt+standard_prompt,
                        max_new_tokens=1000*ratio
                    )
                elif compress_method in ["Qwen2-72B-Instruct_cloud"]:
                    tmp_compress_prompt=Qwen.Qwen_generate_cloud(
                        prompt=Qwen_compress_prompt+standard_prompt,
                    )
                elif compress_method=="Qwen2-72B-Instruct_local_vllm":
                    # response=client.completions.create(  # 使用completions接口
                    #     model="Mixtral-8x7B-Instruct",
                    #     prompt=input_prompt,  # 直接传递原始prompt
                    #     max_tokens=300,
                    #     temperature=0,
                    #     seed=1437
                    # )
                    # tmp_compress_prompt=response.choices[0].text  # 注意字段变化

                    response=client.chat.completions.create(
                        model="Qwen2-72B-Instruct",
                        # messages=[{"role":"user","content":input_prompt}],
                        messages=[
                            {'role':'system','content':'You are a helpful assistant.'},
                            {'role':'user','content':Qwen_compress_prompt+standard_prompt}],
                        max_tokens=int(1000*ratio),
                        temperature=0,
                        seed=1437
                    )
                    tmp_compress_prompt=response.choices[0].message.content

                    # tmp_compress_prompt=Qwen_compress_prompt+standard_prompt
                    # tmp_compress_prompt=tmp_compress_prompt[0:100]
                elif compress_method=="original":
                    tmp_compress_prompt=standard_prompt

                if compress_method not in ["llmlingua","longllmlingua"]:
                    if not compress_question:
                        if dataset=="LongBench":
                            data["context"]=tmp_compress_prompt
                            # print(len(data["context"]))
                            tmp_compress_prompt=question.format(**data)
                            # print(len(tmp_compress_prompt))
                        elif dataset=="RULER_niah":
                            tmp_compress_prompt=question[0]+tmp_compress_prompt+question[1]
                        else:
                            tmp_compress_prompt+=question
                        # tmp_compress_prompt+=question
                revised_prompt_list.append(tmp_compress_prompt)

            if compress_method!="llmlingua":
                if not compress_question:
                    if dataset=="LongBench":
                        data["context"]=standard_prompt
                        standard_prompt=question.format(**data)
                    elif dataset=="RULER_niah":
                        standard_prompt=question[0]+standard_prompt+question[1]
                    else:
                        standard_prompt+=question
                    # standard_prompt+=question


            revised_prompt_list.append(standard_prompt)
            # standard_answer = None
            if dataset in ["GSM8K","hotpotQA"]:
                standard_answer=data["answer"]
            elif dataset=="LongBench":
                standard_answer=data["answers"]
                revised_prompt_list=revised_prompt_list[:-1]
            elif dataset=="RULER_niah":
                standard_answer=data["outputs"]
                revised_prompt_list=revised_prompt_list[:-1]
            # elif dataset=="arXiv":
            #     standard_answer=abstract
            else:
                standard_answer=revised_prompt_list[-1]
                revised_prompt_list=revised_prompt_list[:-1]

            all_revised_prompt_list.append(revised_prompt_list)
            all_standard_answer.append(standard_answer)
            if dataset=="arXiv":
                all_abstract.append(abstract)
    file_name1=folder_path+"/compressed_prompt.json"
    with open(file_name1,'w',encoding='utf-8') as file:
        json.dump(all_revised_prompt_list,file,ensure_ascii=False,indent=4)

    if dataset in ["GSM8K","hotpotQA","LongBench","RULER_niah"]:
        file_name2=folder_path+"/standard_answer.json"
        with open(file_name2,'w',encoding='utf-8') as file:
            json.dump(all_standard_answer,file,ensure_ascii=False,indent=4)
    else:
        file_name2=folder_path+"/standard_prompt.json"
        with open(file_name2,'w',encoding='utf-8') as file:
            json.dump(all_standard_answer,file,ensure_ascii=False,indent=4)
    if dataset in ["arXiv"]:
        file_name2=folder_path+"/abstract.json"
        with open(file_name2,'w',encoding='utf-8') as file:
            json.dump(all_abstract,file,ensure_ascii=False,indent=4)
    print([good,bad])
    return

Decoupled_component.general_line=general_line