import json
import Evaluate
import Load_llm
import Context_match
import Prompt_evaluate
import Decoupled_component

def batch_prompt_evaluate(
    folder_path,
    dataset
):
    if dataset[0:5]=="GSM8K":
        prompt_path="prompt_"+dataset[5:]
        dataset="GSM8K"

    model_path="Llama-2-7b-hf"
    device_map="cuda"
    (model,
     tokenizer,
     context_idxs,
     max_position_embeddings,
     device_map)\
        =(Load_llm.load_llm(
        model_path,
        device_map=device_map,
        load_model_label=False,
    ))

    file_name1=folder_path+"/compressed_prompt.json"
    with open(file_name1,'r',encoding='utf-8') as f:
        compressed_prompts=json.load(f)
    if dataset in ["GSM8K","hotpotQA","arXiv"]:
        for compressed_prompt in zip(compressed_prompts):
            Prompt_evaluate.prompt_evaluate(
                compressed_prompt,
                tokenizer,
                standard_answer=None,
                dataset=dataset
            )
    else:
        file_name2=folder_path+"/standard_prompt.json"
        with open(file_name2,'r',encoding='utf-8') as f:
            answer_lists=json.load(f)
        for compressed_prompt,standard_answer in zip(compressed_prompts,answer_lists):
            compressed_prompt.append(standard_answer)
            Prompt_evaluate.prompt_evaluate(
                compressed_prompt,
                tokenizer,
                standard_answer,
                dataset
            )

def llm_generate_line(
    folder_path,
    standard_answer,
    evaluate_mode,
    multiprocessing_num,
    token_id
):
    if standard_answer==None:
        file_path=folder_path+"/standard_prompt.json"
        output_path=folder_path+"/standard_answer.json"
        batch_generation(
            file_path,
            output_path,
            evaluate_mode,
            multiprocessing_num,
            token_id
        )
        # return
    file_path=folder_path+"/compressed_prompt.json"
    output_path=folder_path+"/llm_output.json"
    batch_generation(
        file_path,
        output_path,
        evaluate_mode,
        multiprocessing_num,
        token_id
    )

def batch_generation(
    file_path,
    output_path,
    evaluate_mode,
    multiprocessing_num,
    token_id
):
    with open(file_path,'r',encoding='utf-8') as f:
        prompt_lists=json.load(f)

    # if isinstance(prompt_lists[0],list):
    #     ratio_num=len(prompt_lists[0])
    # else:
    #     ratio_num=1
    # print(ratio_num)
    ratio_num=len(prompt_lists[0])

    revised_prompt_list=[]
    for item in prompt_lists:
        if isinstance(item,list):
            revised_prompt_list=revised_prompt_list+item
        else:
            revised_prompt_list.append(item)

    model_path="Llama-2-7b-hf"
    device_map="cuda"

    if evaluate_mode=="llama2-7b":
        load_model_label=True
    else:
        load_model_label=False
    (model,
     tokenizer,
     context_idxs,
     max_position_embeddings,
     device_map)\
        =(Load_llm.load_llm(
        model_path,
        device_map=device_map,
        load_model_label=load_model_label,
    ))
    if evaluate_mode=="Qwen2-72B-Instruct":
        from transformers import AutoModelForCausalLM
        model_name="Qwen/Qwen2-72B-Instruct"
        model=AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_name,
            torch_dtype="auto",
            device_map="auto"
        )

    if evaluate_mode in ["llama2-7b","Qwen2-72B-Instruct"]:
        output_list=[]
        for revised_prompt in revised_prompt_list:
            tmplength,tmpoutput=Evaluate.local_llm_generate(revised_prompt,
                                                            tokenizer,
                                                            model,
                                                            mode=evaluate_mode,
                                                            max_tokens=300)
            output_list.append((tmplength,tmpoutput))

    if evaluate_mode in ["mixtral_local","Qwen2-72B-Instruct_local_vllm","Llama-3-70B-Instruct_local_vllm"]:
        # use Mixtral-8x7B-Instruct-v0.1
        # from openai import OpenAI
        # from concurrent.futures import ThreadPoolExecutor
        # client=OpenAI(base_url="http://localhost:8000/v1",api_key="none")
        # def process_prompt(input_prompt):
        #     inputs=tokenizer(input_prompt,return_tensors="pt")
        #     length=inputs.input_ids.shape[1]
        #     response=client.chat.completions.create(
        #         model="Mixtral-8x7B-Instruct",
        #         messages=[{"role":"user","content":input_prompt}],
        #         max_tokens=300,
        #         temperature=0,
        #         seed=1437
        #     )
        #     return (length,response.choices[0].message.content)
        #
        # with ThreadPoolExecutor(max_workers=64) as executor:
        #     output_list=list(executor.map(process_prompt,revised_prompt_list))

        from openai import OpenAI
        from concurrent.futures import ThreadPoolExecutor
        client=OpenAI(base_url="http://localhost:8000/v1",api_key="none")

        if evaluate_mode=="mixtral_local":
            model_name="Mixtral-8x7B-Instruct"
        elif evaluate_mode=="Qwen2-72B-Instruct_local_vllm":
            model_name="Qwen2-72B-Instruct"
        elif evaluate_mode=="Llama-3-70B-Instruct_local_vllm":
            model_name="Llama-3-70B-Instruct"
        def process_prompt(input_prompt):
            inputs=tokenizer(input_prompt,return_tensors="pt")
            length=inputs.input_ids.shape[1]
            if model_name=="Qwen2-72B-Instruct":
                response=client.chat.completions.create(
                    model=model_name,
                    # messages=[{"role":"user","content":input_prompt}],
                    messages=[
                        {"role":"system","content":"You are a helpful assistant."},
                        {"role":"user","content":input_prompt}
                    ],
                    max_tokens=300,
                    temperature=0,
                    seed=1437
                )
                response_text=response.choices[0].message.content
            else:
                response=client.completions.create(  # 使用completions接口
                    # model="Mixtral-8x7B-Instruct",
                    model=model_name,
                    prompt=input_prompt,  # 直接传递原始prompt
                    max_tokens=300,
                    temperature=0,
                    seed=1437,
                    timeout=60000
                )d
                response_text=response.choices[0].text

            # return (length,response.choices[0].text)  # 注意字段变化

            return (length,response_text)


        with ThreadPoolExecutor(max_workers=64) as executor:
            output_list=list(executor.map(process_prompt,revised_prompt_list))


    else:
        from functools import partial
        from multiprocessing import Pool
        import os
        os.environ["TOKENIZERS_PARALLELISM"]="false"
        path="tokens/llmtokens.txt"
        token_list=[]
        with open(path,'r',encoding="utf-8") as file:
            for line in file:
                if line[-1]=="\n":
                    line=line[:-1]
                token_list.append(line)
        token=token_list[token_id]

        mode_llm_generate=partial(Evaluate.hfp_llm_generate,
                                  tokenizer=tokenizer,
                                  mode=evaluate_mode,
                                  max_tokens=300,
                                  token=token)
        with Pool(processes=multiprocessing_num) as pool:
            output_list=pool.map(mode_llm_generate,revised_prompt_list)

    i=ratio_num
    nested_list=[]
    for item in output_list:
        if i<ratio_num:
            nested_list[-1].append(item)
            i+=1
        else:
            nested_list.append([item])
            i=1

    # print(nested_list)
    # for item in nested_list[0]:
    #     print(item)
    #     print("####")

    with open(output_path,'w',encoding='utf-8') as file:
        json.dump(nested_list,file,ensure_ascii=False,indent=4)

def batch_scoring(
    folder_path,
    standard_answer,
    dataset
):

    if standard_answer==None:
        standard_answer=folder_path

    arXiv_scoring_method="1"
    if dataset[0:5]=="GSM8K":
        dataset="GSM8K"
    elif dataset[0:5]=="arXiv":
        arXiv_scoring_method=dataset[5:]
        dataset="arXiv"
    # print(dataset)

    file_name1=folder_path+"/llm_output.json"
    with open(file_name1,'r',encoding='utf-8') as f:
        output_lists=json.load(f)

    # file_name2=standard_answer+"/standard_answer.json"
    # with open(file_name2,'r',encoding='utf-8') as f:
    #     answer_lists=json.load(f)
    # if dataset not in ["GSM8K","hotpotQA","arXiv"]:
    #     answer_lists=answer_lists[0]
    # # print(len(output_lists),len(answer_lists))
    #
    # if dataset in ["GSM8K","hotpotQA","arXiv"]:
    #     # print(dataset)
    #     for output_list,standard_answer in zip(output_lists,answer_lists):
    #         Evaluate.evaluate1(
    #             output_list,
    #             standard_answer,
    #             dataset
    #         )
    #         # break
    # else:
    #     for output_list,standard_answer in zip(output_lists,answer_lists):
    #         # print(output_list,standard_answer)
    #         output_list.append(standard_answer)
    #         # print(output_list)
    #         Evaluate.evaluate1(
    #             output_list,
    #             standard_answer,
    #             dataset
    #         )
    #         # break

    file_name2=standard_answer+"/standard_answer.json"
    with open(file_name2,'r',encoding='utf-8') as f:
        answer_lists=json.load(f)
    if dataset not in ["GSM8K","hotpotQA"]:
        answer_lists=answer_lists[0]

    if dataset=="arXiv":
        file_name3=standard_answer+"/abstract.json"
        with open(file_name3,'r',encoding='utf-8') as f:
            abstract_lists=json.load(f)
            abstract_lists=abstract_lists[0]
    # print(len(output_lists),len(answer_lists))

    if dataset in ["GSM8K","hotpotQA"]:
        # print(dataset)
        if dataset=="hotpotQA":
            distributed_label=True
        if distributed_label==False:
            for output_list,standard_answer in zip(output_lists,answer_lists):
                Evaluate.evaluate1(
                    output_list,
                    standard_answer,
                    dataset
                )
                # break
        else:
            import decp24
            decp24.distributed_eval(output_lists,answer_lists,dataset)


    elif dataset!="arXiv" or arXiv_scoring_method=="1":
        for output_list,standard_answer in zip(output_lists,answer_lists):
            # print(output_list,standard_answer)
            output_list.append(standard_answer)
            # print(output_list)
            # print(standard_answer)
            # print("\n\n")
            # print(output_list)
            Evaluate.evaluate1(
                output_list,
                standard_answer,
                dataset
            )
            # break
    else:
        for output_list,standard_answer in zip(output_lists,answer_lists):
            # print(output_list,standard_answer)
            output_list.append(standard_answer)
            # print(output_list)
            Evaluate.evaluate1(
                output_list,
                abstract_lists,
                dataset
            )
            # break

def batch_context_match(
    folder_path
):
    file_path=folder_path+"/compressed_prompt.json"
    with open(file_path,'r',encoding='utf-8') as f:
        prompt_lists=json.load(f)
    # ratio_num=len(prompt_lists[0])
    # output_list=[]

    file_name2=folder_path+"/standard_prompt.json"
    with open(file_name2,'r',encoding='utf-8') as f:
        answer_lists=json.load(f)
        # answer_lists=answer_lists[0]

    for revised_prompt_list,answer in zip(prompt_lists,answer_lists):
        # print(revised_prompt_list)
        # print(answer)
        for item in revised_prompt_list:
            context_match_pair1=Context_match.context_match_pair(item,answer)
            context_match_pair1.matching()
            print(context_match_pair1.match_length)
            print(context_match_pair1.match_context)

    # i=ratio_num
    # nested_list=[]
    # for item in output_list:
    #     if i<ratio_num:
    #         nested_list[-1].append(item)
    #         i+=1
    #     else:
    #         nested_list.append([item])
    #         i=1
    #
    # with open(output_path,'w',encoding='utf-8') as file:
    #     json.dump(nested_list,file,ensure_ascii=False,indent=4)




Decoupled_component.batch_prompt_evaluate=batch_prompt_evaluate
Decoupled_component.llm_generate_line=llm_generate_line
Decoupled_component.batch_generation=batch_generation
Decoupled_component.batch_scoring=batch_scoring
Decoupled_component.batch_context_match=batch_context_match
