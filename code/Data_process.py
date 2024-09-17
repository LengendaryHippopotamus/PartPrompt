import copy
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
        else:
            prompt=data[0]
            question=data[1]
        while(prompt[-2:]!="\n\n"):
            prompt+="\n"
        if compress_question:
            prompt+=question
        split_text = prompt.split("\n")
        sentences = []
        endlabels = []
        for item in split_text:
            if item != "":
                sentences.append(item)
                endlabels.append(1)
            elif sentences != []:
                endlabels[-1] += 1
        for i in range(len(sentences)):
            sentence = sentences[i].split(". ")
            for sent in sentence:
                sentences_list.append(sent + ".")
                endlabels_list.append(0)
            sentences_list[-1] = sentences_list[-1][:-1]
            endlabels_list[-1] = min(2, endlabels[i])
        endlabels_list[-1] = 1
        if not compress_question:
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
            truncate_label=len(endlabels_list)
    if sum_of_length<6000:
        badlabel=1

    if compress_question:
        sentences_list.append("Task: Please write an abstract for the above article.")
        endlabels_list[-1] = 1
        endlabels_list.append(0)
    else:
        question = "\nTask: Please write an abstract for the above article."
    if sent_simplify_label:
        return sentences_list,endlabels_list,question,abstract,sum_of_length,badlabel
    else:
        return sentences_list[0:truncate_label],endlabels_list[0:truncate_label],question,abstract,sum_of_length,badlabel