import copy
import json

def data_process(data,
                 dataset,
                 compress_question,
                 GSM8K_prompt,
                 tokenizer
                 ):
    sentences_list=[]
    endlabels_list=[]
    question=""
    badlabel=0
    if dataset=="hotpotQA":
        for paragraph in data["context"]:
            # title = paragraph[0]
            sentences = paragraph[1]
            length=len(sentences)
            for idex,sentence in enumerate(sentences):
                endlabel=1
                if idex==length-1:
                    endlabel=2
                sentences_list.append(sentence)
                endlabels_list.append(endlabel)
        if not compress_question:
            question="\nQuestion:"+data["question"]
        else:
            sentences_list.append("\nQuestion:"+data["question"])
            endlabels_list[-1]=1
            endlabels_list.append(0)

    elif dataset == "arXiv" or dataset == "truncate_arXiv":
        bodylabel = 0
        split_text = data["text"].split("\n")
        sentences = []
        endlabels = []
        for item in split_text:
            if "§" in item:
                bodylabel = 1
            if bodylabel == 1 and "§" not in item:
                if item != "":
                    sentences.append(item)
                    endlabels.append(1)
                elif sentences != []:
                    endlabels[-1] += 1
        sum_of_length = 0
        for i in range(len(sentences)):
            sum_of_length += len(tokenizer.tokenize(sentences[i]))
            if dataset == "truncate_arXiv" and sum_of_length > 3000:
                break
            sentence = sentences[i].split(". ")
            for sent in sentence:
                sentences_list.append(sent + ".")
                endlabels_list.append(0)
            sentences_list[-1] = sentences_list[-1][:-1]
            endlabels_list[-1] = min(2, endlabels[i])
        if compress_question:
            sentences_list.append("Task: Please write a summary for the above document.")
            endlabels_list[-1] = 1
            endlabels_list.append(0)
        else:
            question = "\nTask: Please write a summary for the above document."

    elif dataset == "PeopleDaily":
        sentences_list=data["content"]
        endlabels_list=[min(2,ex) for ex in data["label"]]
        badlabel=0
        if compress_question:
            sentences_list.append("Task: Please write a summary for the above document.")
            endlabels_list[-1] = 1
            endlabels_list.append(0)
        else:
            question = "\nTask: Please write a summary for the above document."

    elif dataset=="MedicalConsensus":
        sentences_list=data["content"]
        endlabels_list=[min(2,ex) for ex in data["label"]]
        badlabel=0
        if compress_question:
            sentences_list.append("Task: Please write a summary for the above document.")
            endlabels_list[-1]=1
            endlabels_list.append(0)
        else:
            question="\nTask: Please write a summary for the above document."

    elif dataset == "CodeNet":
        sentences_list=data["content"]
        endlabels_list=[min(2,ex) for ex in data["label"]]
        badlabel=0
        if compress_question:
            sentences_list.append("Task: Please write a summary for the above python code.")
            endlabels_list[-1] = 1
            endlabels_list.append(0)
        else:
            question = "\nTask: Please write a summary for the above python code."
    else:
        if dataset=="BBCnews":
            prompt=data["content"]
            length = len(tokenizer.tokenize(prompt))
            if length > 3800:
                badlabel = 1
            question="Task: Please write a summary for the above document."
        elif dataset=="GSM8K":
            prompt=GSM8K_prompt
            question='Question: '+data["question"]
        elif dataset=="LongBench":
            prompt=data['context']
            question=data['input']
            dataset2prompt = json.load(open("dataset/dataset2prompt.json", "r"))
        elif dataset=="RULER_niah":
            context=data["input"]
            len1=len("A special magic number is hidden within the following text. Make sure to memorize it. I will quiz you about the number afterwards.\n")
            import re
            pattern=r"\nWhat is the special magic number for [a-zA-Z- ]+ mentioned in the provided text\?$"
            match=re.search(pattern,context)
            if match:
                suffix=match.group()
                prefix=context[:-len(suffix)]
            else:
                print("匹配失败：未找到符合条件的结尾部分")
                print(context)

            prompt=prefix[len1:]
            question=["A special magic number is hidden within the following text. Make sure to memorize it. I will quiz you about the number afterwards.\n",suffix]

        else:
            prompt=data[0]
            question=data[1]
        while(prompt[-2:]!="\n\n"):
            prompt+="\n"
        if compress_question:
            if dataset=="LongBench":
                prompt_format=dataset2prompt[data['dataset']]
                prompt=prompt_format.format(**data)
            elif dataset=="RULER_niah":
                prompt=question[0]+prompt+question[1]
            else:
                prompt+=question

        split_text = prompt.split("\n")
        # print(split_text)
        sentences = []
        endlabels = []
        for item in split_text:
            if item != "":
                sentences.append(item)
                endlabels.append(1)
            elif sentences != []:
                endlabels[-1] += 1
        # print(endlabels)
        for i in range(len(sentences)):
            sentence = sentences[i].split(". ")
            for sent in sentence:
                if dataset=="LongBench":
                    sent_zh=sent.split("。")
                    sentences_list+=[sent_zh_i+"。" for sent_zh_i in sent_zh[:-1]]
                    sentences_list.append(sent_zh[-1]+".")
                    endlabels_list+=[0]*len(sent_zh)
                else:
                    sentences_list.append(sent + ".")
                    endlabels_list.append(0)
            sentences_list[-1] = sentences_list[-1][:-1]
            endlabels_list[-1] = min(2, endlabels[i])

        # endlabels_list[-1] = 2
        # if compress_question:
        #     endlabels_list[-1] = 1
        # else:
        #     endlabels_list[-1] = 2
        endlabels_list[-1] = 1
        if not compress_question:
            if dataset=="LongBench":
                question=dataset2prompt[data['dataset']]
            elif dataset=="RULER_niah":
                pass
            else:
                question="\n"+question

    # for coherence
    # new_sent_list=[]
    # length_sum=0
    # for sent in sentences_list:
    #     length_sum+=len(tokenizer.tokenize(sent))
    #     if length_sum>500:
    #         break
    #     new_sent_list.append(sent)
    # if len(new_sent_list)<2:
    #     badlabel=1
    # return new_sent_list,endlabels_list[0:len(new_sent_list)],"",badlabel

    # question=""

    return sentences_list,endlabels_list,question,badlabel


def data_process_for_arXiv(
        data,
        dataset,
        compress_question,
        tokenizer,
        sent_simplify_label,
        ):
    sentences_list=[]
    endlabels_list=[]
    # truncate_sentence_list=[]
    # truncate_endlabels_list=[]
    question=""
    badlabel=0
    bodylabel = 0

    content=data["text"].split("§")[0]
    content_list=content.split("\n")
    length=0
    abstract=""
    for item in content_list:
        if item[0:5]!="=====" and len(item)>length:
            abstract=item
            length=len(item)
    if length<200:
        badlabel=1
        return sentences_list,endlabels_list,question,abstract,0,badlabel

    split_text = data["text"].split("\n")
    sentences = []
    endlabels = []
    for item in split_text:
        if "§" in item:
            bodylabel = 1
        if bodylabel == 1 and "§" not in item:
            if item != "":
                sentences.append(item)
                endlabels.append(1)
            elif sentences != []:
                endlabels[-1] += 1
    sum_of_length = 0
    truncate_label=0
    sum_of_length_list=[]
    for i in range(len(sentences)):
        sum_of_length += len(tokenizer.tokenize(sentences[i]))
        sum_of_length_list.append(sum_of_length)

        sentence = sentences[i].split(". ")
        for sent in sentence:
            sentences_list.append(sent + ".")
            endlabels_list.append(0)
        sentences_list[-1] = sentences_list[-1][:-1]
        endlabels_list[-1] = min(2, endlabels[i])

        if sum_of_length < 3000:
            # truncate_sentence_list=sentences_list
            # truncate_endlabels_list=endlabels_list
            truncate_label=len(endlabels_list)

    if sum_of_length<6000:
        badlabel=1

    if compress_question:
        sentences_list.append("Task: Please write an abstract for the above article.")
        endlabels_list[-1] = 1
        endlabels_list.append(0)
    else:
        question = "\nTask: Please write an abstract for the above article."

    # print(truncate_label,sum_of_length_list)
    if sent_simplify_label:
        return sentences_list,endlabels_list,question,abstract,sum_of_length,badlabel
    else:
        return sentences_list[0:truncate_label],endlabels_list[0:truncate_label],question,abstract,sum_of_length,badlabel