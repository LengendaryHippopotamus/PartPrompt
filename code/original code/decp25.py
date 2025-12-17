# 2024/1/1 21:54
import Data_loader
import Data_process
import Load_llm
import Sentence_process

def sent_length_value_exp(
    dataset,
    auto_para_label=[0,1,2],
    compress_question=False,
    triple_label=False,
    without_infoentropy=False,
    sent_simplify_label=True,
    device_map="cuda",
):
    if dataset[0:5]=="GSM8K":
        prompt_path="prompt_"+dataset[5:]
        dataset="GSM8K"
    all_data=Data_loader.data_loader(dataset)
    if dataset == "GSM8K":
        GSM8K_prompt = open("dataset/gsm8k_prompt/"+prompt_path+".txt", 'r').read()
        print("GSM8K_prompt",prompt_path)
    else:
        GSM8K_prompt=None

    model_path="Llama-2-7b-hf"

    if without_infoentropy:
        load_model_label=False
    else:
        load_model_label=True
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

    good=0
    bad=0
    sent_length_value=[]
    for dex, data in enumerate(all_data):
        if dex>500 and dataset in ["BBCnews","LongBench"]:
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
                    sent_simplify_label,
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
                GSM8K_prompt,
                tokenizer
            )

        if badlabel==0:
            past_key_values=None
            past_sentence=""
            for sentence,endlabel in zip(sentences_list,endlabels_list):
                (tmplabel,
                 tmpwordlist,
                 tmpedge,
                 tmpinfoentropy,
                 tmplength_factor,
                 tmptriple_text,
                 past_key_values,
                 past_sentence) = Sentence_process.sentence_process(
                    sentence,
                    endlabel,
                    triple_label,
                    auto_para_label,
                    without_infoentropy,
                    tokenizer,
                    device_map,
                    max_position_embeddings,
                    model,
                    past_key_values,
                    past_sentence
                )
                if sent_simplify_label==True:
                    past_key_values=None
                    past_sentence=""
                if tmplabel == 1:
                    badlabel = 1
                    continue
                elif tmplabel == 2:
                    continue
                else:
                    sent_length_value.append((len(tmpwordlist),sum(tmpinfoentropy)))
            bad += badlabel
            if dataset=="arXiv":
                good+=1
            else:
                good += (1 - badlabel)
        else:
            bad += badlabel
            good += (1 - badlabel)
            continue

    def save_data_point(filename,x,y):
        with open(filename,'a') as f:
            f.write(f"{x},{y}\n")

    filename="sent_length_value.csv"
    for x,y in sent_length_value:
        save_data_point(filename,x,y)

    print(f"已保存 {len(sent_length_value)} 个数据点到 {filename}")

    return
