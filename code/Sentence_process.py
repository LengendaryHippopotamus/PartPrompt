import math
import re
import torch
import Infoentropy
from sentence_parse import CoreNLP_parse
def sentence_process(
    sentence,
    endlabel,
    auto_para_label,
    without_infoentropy,
    tokenizer,
    device_map,
    max_position_embeddings,
    model,
    past_key_values,
    past_sentence
):
    badlabel=0
    while sentence != "" and (sentence[-1] == " " or sentence[-1]=="\t"):
        sentence = sentence[0:-2]
    while sentence != "" and (sentence[0] == " " or sentence[0]=="\t"):
        sentence = sentence[1:]
    if sentence == "":
        return 2,-1,-1,-1,-1,-1,past_key_values,past_sentence
    else:
        triple_text = ""
        try:
            edge, wordlist = CoreNLP_parse.parse_sentence(sentence.split(" "))
        except BaseException as e:
            print([sentence])
            return 2,-1,-1,-1,-1,-1,past_key_values,past_sentence

        if len(wordlist)>1:
            if wordlist[-1]=="." and wordlist[-2][-1]==".":
                sentence+="."
        tokenized_text = tokenizer.tokenize(sentence)
        import copy
        original_wordlist=copy.deepcopy(wordlist)
        endlabel=auto_para_label[endlabel]
        if endlabel==1:
            sentence+="\n"
            wordlist.append("\n")
            tokenized_text.append("\n")
            edge[0].append(edge[1][0])
            edge[1].append(len(wordlist))
        elif endlabel==2:
            sentence+="\n\n"
            wordlist+=["\n","\n"]
            tokenized_text+=["\n","\n"]
            edge[0]+=[edge[1][0],edge[0][0]]
            edge[1]+=[len(wordlist)-1,len(wordlist)]
        if without_infoentropy:
            infoentropy=torch.ones([len(tokenizer.tokenize(sentence))])
            past_key_values=None
            past_sentence=""
        else:
            (infoentropy,
             past_key_values,
             past_sentence
             ) = Infoentropy.infoentropy(
                sentence,
                triple_text,
                tokenizer,
                device_map,
                max_position_embeddings,
                model,
                past_key_values=past_key_values,
                past_sentence=past_sentence,
                return_kv=True,
                end=None,
            )
        i = 0
        j = 0
        matched_infoe = []
        length_factor = []
        tmptext1 = ""
        tmptext2 = ""
        n = 0
        m = 0
        tmpinfo = 0
        _label=False
        insert_list=[]
        while (1):
            if tmptext1 < tmptext2:
                tmptext1 += wordlist[i]
                n += 1
                i += 1
            elif tmptext1 > tmptext2 or tmptext1 == "":
                if tmptext1 == "":
                    tmptext1 = wordlist[i]
                    i += 1
                    n = 1
                if tokenized_text[j] in ["\xa0","▁\xa0","\u200e"]:
                    wordlist.insert(i-1, tokenized_text[j])
                    i += 1
                    j += 1
                    matched_infoe.append(infoentropy[j].item())
                    insert_list.append(i-1)
                    length_factor.append(1)
                elif re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j]):
                    length = len(tmptext2)
                    if tmptext1[0:length] != tmptext2:
                        badlabel = 1
                        break
                    utftext = ""
                    while (1):
                        if j >= len(tokenized_text) or (not re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j])):
                            badlabel = 1
                            j = len(tokenized_text) + 1
                            break
                        utftext += re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j]).group()[3:5]
                        tmpinfo += infoentropy[j].item()
                        m += 1
                        j += 1
                        try:
                            tmp_character = bytes.fromhex(utftext).decode("utf-8")
                            if tmp_character == tmptext1[length]:
                                tmptext2 += tmp_character
                                break
                        except BaseException as e:
                            pass
                else:
                    if tokenized_text[j][0] == "▁":
                        if wordlist[i - 1][0] != "▁":
                            wordlist[i - 1] = "▁" + wordlist[i - 1]
                        tmptext2 += tokenized_text[j][1:]
                    else:
                        tmptext2 += tokenized_text[j]
                    tmpinfo += infoentropy[j].item()
                    m += 1
                    j += 1
            if (tmptext1 == tmptext2 and tmptext1 != ""):
                for k in range(n):
                    matched_infoe.append(tmpinfo / n)
                    length_factor.append(math.ceil(m / n))
                tmptext1 = ""
                tmptext2 = ""
                tmpinfo = 0
                n = 0
                m = 0
                _label = False
            if i >= len(wordlist) and j >= len(tokenized_text):
                break
            elif (i >= len(wordlist) and tmptext1 <= tmptext2) or (j >= len(tokenized_text) and tmptext1 >= tmptext2):
                badlabel = 1
                break
            elif i>1000 or j>1000:
                badlabel = 1
                break
        for insert_i in insert_list:
            for l in range(len(edge[0])):
                if edge[0][l]>=insert_i:
                    edge[0][l]+=1
            for l in range(len(edge[1])):
                if edge[1][l]>=insert_i:
                    edge[1][l]+=1
        for insert_i in insert_list:
            edge[0].append(insert_i+1)
            edge[1].append(insert_i)
    if len(wordlist)!=len(matched_infoe):
        badlabel=1
    return badlabel,wordlist,edge,matched_infoe,length_factor,triple_text,past_key_values,past_sentence