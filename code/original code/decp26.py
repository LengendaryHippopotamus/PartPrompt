import json
from pathlib import Path

def length_eval(folder_path):
    file_name1=folder_path+"/compressed_prompt.json"
    with open(file_name1,'r',encoding='utf-8') as f:
        compressed_prompt_lists=json.load(f)
    model_path="Llama-2-7b-hf"
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(model_path)

    total_length=[[] for x in range(len(compressed_prompt_lists[0]))]

    for prompt_list in compressed_prompt_lists:
        for i,prompt in enumerate(prompt_list):
            prompt_len=len(tokenizer.tokenize(prompt))
            print(prompt_len)
            total_length[i].append(prompt_len)
        print("####")
    # print(total_length)
    # print(sum(total_length),len(total_length),sum(total_length)/len(total_length))

    with open(folder_path+"/length.json",'w',encoding='utf-8') as file:
        json.dump(total_length,file,ensure_ascii=False,indent=4)

    return



