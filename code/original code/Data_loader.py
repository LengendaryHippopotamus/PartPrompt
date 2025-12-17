# 2024/1/1 22:10
import json

def data_loader(dataset):
    if(dataset=="hotpotQA"):
        file_path = 'dataset/hotpot_dev_distractor_v1.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    elif(dataset=="GSM8K"):
        from datasets import load_dataset, load_from_disk
        gsm8k = load_from_disk("dataset/gsm8k")
        return gsm8k["test"]
    elif(dataset=="arXiv" or dataset=="truncate_arXiv"):

        file_path=r"dataset/arxiv_merged4.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        # print(len(all_data))
        return all_data
    elif (dataset == "BBCnews"):
        file_path=r"dataset/BBC_merged2.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    elif (dataset == "PeopleDaily"):
        file_path=r"dataset/PeopleDaily.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    elif (dataset == "MedicalConsensus"):
        file_path=r"dataset/MedicalExpertConsensus2.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    elif (dataset == "CodeNet"):
        file_path=r"dataset/CodeNetPython.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    elif dataset=="LongBench":
        import os
        if os.path.exists("dataset/LongBench.json"):
            with open("dataset/LongBench.json",'r',encoding='utf-8') as f:
                data=json.load(f)
                return data

        # data_dir=r"D:\document\code\hierarchical prompt\20250510\dataset\LongBench"
        data_dir=r"dataset/LongBench"
        longbench_datasets_list=["narrativeqa","qasper","multifieldqa_en","multifieldqa_zh","hotpotqa","2wikimqa","musique",
                                 "dureader","gov_report","qmsum","multi_news","vcsum","trec","triviaqa","samsum","lsht",
                                 "passage_count","passage_retrieval_en","passage_retrieval_zh","lcc","repobench-p"]
        datalist=[]
        for longbench_dataset in longbench_datasets_list:
            # path=data_dir+"\data\\"+longbench_dataset+".jsonl"
            path=data_dir+"/data/"+longbench_dataset+".jsonl"
            with open(path,'r',encoding='utf-8') as file:
                for line in file:
                    data=json.loads(line)
                    datalist.append(data)
        import random
        random.seed(1437)
        random.shuffle(datalist)

        with open("dataset/LongBench.json",'w',encoding='utf-8') as f:
            json.dump(datalist[0:500],f,ensure_ascii=False,indent=4)

        return datalist[0:500]
    elif (dataset == "RULER_niah"):
        file_name="dataset/RULER_niah.json"
        with open(file_name,"r",encoding="utf-8") as file:
            data=json.load(file)
        return data
    return
# data_process("BBCnews")