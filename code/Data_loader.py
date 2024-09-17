import json
def data_loader(dataset):
    # print(dataset)
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
        return all_data
    elif (dataset == "BBCnews"):
        file_path=r"dataset/BBC_merged.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        return all_data
    return