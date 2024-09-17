import json
import Data_loader
import Data_process
import Edge_process
import Load_llm
import Infotree
import Sentence_process
import Overall_infoentropy
def hierarchical_prompt(
    dataset,
    mode,
    ratio,
    auto_para_label=[0,1,2],
    compress_question=False,
    overall_parse_compress_label=False,
    adjust_ratio_list=[0.0,0.0,0.0,0.0,0.0,0.0],
    first_word_adjust_label=False,
    hierarchical_global_label=True,
    tree_propagation_label=True,
    propagation_ratio_list=[0.95,1,0.6,1,1],
    triple_label=False,
    without_infoentropy=False,
    sent_simplify_label=True,
    without_tree=False,
    device_map="cuda",
    folder_path="",
):
    if dataset[0:5]=="GSM8K":
        prompt_path="prompt_"+dataset[5:]
        dataset="GSM8K"
    all_data=Data_loader.data_loader(dataset)
    ratio_list = ratio.split(",")
    if dataset == "GSM8K":
        # prompt_path="prompt_original"
        GSM8K_prompt = open("dataset/gsm8k_prompt/"+prompt_path+".txt", 'r').read()
        print("GSM8K_prompt",prompt_path)
    else:
        GSM8K_prompt=None
    model_path="/model/llama-hf"
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
    all_revised_prompt_list=[]
    all_standard_answer=[]
    all_abstract=[]
    for dex, data in enumerate(all_data):
        if dex>500 and dataset in ["hotpotQA","BBCnews"]:
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
            wordlist = []
            edge = []
            infoentropy = []
            length_factor = []
            triple_text = []
            new_endlabel_list=[]
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
                    wordlist.append(tmpwordlist)
                    edge.append(tmpedge)
                    infoentropy.append(tmpinfoentropy)
                    length_factor.append(tmplength_factor)
                    triple_text.append(tmptriple_text)
                    new_endlabel_list.append(endlabel)
            bad += badlabel
            if dataset=="arXiv":
                good+=1
            else:
                good += (1 - badlabel)
        else:
            bad += badlabel
            good += (1 - badlabel)
            continue
        if badlabel==0 or dataset=="arXiv" or dataset=="truncate_arXiv" or badlabel==1:
            new_endlabel_list[-1]=2
            if adjust_ratio_list!=[0.0,0.0,0.0,0.0,0.0,0.0]:
                infoentropy=Overall_infoentropy.adjusted_infoe(
                    infoentropy,
                    new_endlabel_list,
                    adjust_ratio_list,
                    first_word_adjust_label
                )
            (wordlist,
             edge,
             infoentropy,
             length_factor) = Edge_process.edge_process(
                wordlist,
                edge,
                infoentropy,
                length_factor,
                overall_parse_compress_label,
                new_endlabel_list,
                hierarchical_global_label
                )
            tmplength=len(edge)
            golden_compress_list=[]
            for j in range(tmplength):
                infomation_tree=Infotree.infotree(
                    infoentropy[j],
                    edge[j],
                    length_factor[j],
                    without_infoentropy,
                    propagation_ratio_list=propagation_ratio_list,
                    text=wordlist[j],
                    without_tree=without_tree
                )
                infomation_tree.construct()
                # infomation_tree.tree_plot()
                if tree_propagation_label:
                    infomation_tree.rootward_propagation()
                    # infomation_tree.tree_plot()
                    infomation_tree.leafward_propagation()
                    # infomation_tree.tree_plot()
                golden_compress=infomation_tree.compressline()
                golden_compress_list.append(golden_compress)
            revised_prompt_list=[]
            for ratio in ratio_list:
                revised_prompt = ""
                ratio=float(ratio)
                for j,golden_compress in enumerate(golden_compress_list):
                    if golden_compress != -1:
                        length=len(golden_compress)-1
                        if dataset=="arXiv":
                            ratio=(3000/length)*ratio
                        if mode=="tokens":
                            reserved_token = sorted(golden_compress[int(ratio * length + 0.49999)][1:])
                        else:# mode=="infoentropy"
                            truncate_label=0
                            for i in range(1,length+1):
                                truncate_label = i
                                if abs(golden_compress[i][0]/golden_compress[-1][0]-ratio)>abs(golden_compress[i-1][0]/golden_compress[-1][0]-ratio):
                                    break
                            reserved_token = sorted(golden_compress[truncate_label-1][1:])
                        reserved_text = ""
                        for i in reserved_token:
                            item = wordlist[j][i]
                            reserved_text += item
                        revised_prompt+=reserved_text
                if not compress_question:
                    revised_prompt+=question
                revised_prompt=revised_prompt.replace("▁"," ")
                revised_prompt = revised_prompt.replace("\n ", "\n")
                if revised_prompt[0]==" ":
                    revised_prompt=revised_prompt[1:]
                revised_prompt_list.append(revised_prompt)
            standard_prompt=""
            for sentence, endlabel in zip(sentences_list, endlabels_list):
                if standard_prompt!="" and standard_prompt[-1] not in [" ","\n"]:
                    standard_prompt+=" "
                standard_prompt+=sentence
                for i in range(
                    auto_para_label[endlabel]
                ):
                    standard_prompt+="\n"
            if not compress_question:
                standard_prompt+=question
            revised_prompt_list.append(standard_prompt)
            # standard_answer = None
            if dataset=="GSM8K":
                standard_answer=data["answer"]
            elif dataset=="hotpotQA":
                standard_answer=data["answer"]
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
    if dataset in ["GSM8K","hotpotQA"]:
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