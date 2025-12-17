# 2024/3/7 23:20
import math
import re
import torch
import Infoentropy
from sentence_parse import CoreNLP_parse

# import text2graph.hrt
def sentence_process(
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
):
    badlabel=0
    while sentence != "" and (sentence[-1] == " " or sentence[-1]=="\t"):
        sentence = sentence[0:-2]
    while sentence != "" and (sentence[0] == " " or sentence[0]=="\t"):
        sentence = sentence[1:]
    if sentence == "":
        return 2,-1,-1,-1,-1,-1,past_key_values,past_sentence
    else:
        # if triple_label:
        #     hrt_pool = text2graph.hrt.get_graph(sentence)
        #     if hrt_pool == []:
        #         triple_text = ""
        #     else:
        #         triple_text = "(" + hrt_pool[0][0] + ", " + hrt_pool[0][1] + ", " + hrt_pool[0][2] + ")"
        # else:
        #     triple_text = ""
        triple_text = ""
        try:
            edge, wordlist = CoreNLP_parse.parse_sentence(sentence.split(" "))
        except BaseException as e:
            print(e)
            print([sentence])
            return 2,-1,-1,-1,-1,-1,past_key_values,past_sentence

        if len(wordlist)>1:
            if wordlist[-1]=="." and wordlist[-2][-1]==".":
                sentence+="."
        tokenized_text = tokenizer.tokenize(sentence)

        if tokenizer.name_or_path!="Llama-2-7b-hf":
            # for i in range(len(tokenized_text)):
            #     if tokenized_text[i][0]=="Ġ":
            #         tokenized_text[i]="▁"+tokenized_text[i][1:]
            #     if tokenized_text[i]=="Ċ":
            #         tokenized_text[i]="\n"

            tokenized_text=clean_bbpe_tokens(tokenized_text)

        import copy
        original_wordlist=copy.deepcopy(wordlist)

        # endlabel=min(endlabel,auto_para_label)
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

        # past_key_values=None
        # past_sentence=""

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
        # print(wordlist, tokenized_text,infoentropy)
        # print(past_sentence)

        # print(len(tokenized_text),infoentropy.shape)
        # tmp_tokenized_text=tokenizer.tokenize(sentence)
        # print(tmp_tokenized_text)
        # print(tokenized_text)

        # for j in range(len(tokenized_text)):
        #     try:
        #         if tokenized_text[j] != "":
        #             if tokenized_text[j][0] == "▁":
        #                 tokenized_text[j] = tokenized_text[j][1:]
        #     except BaseException as e:
        #         print(j, len(tokenized_text), tokenized_text)
        #         badlabel = 1

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

        # print(wordlist)
        # print(tokenized_text)
        while (1):
            # try:
            #     print(i, j, [tmptext1], [tmptext2])
                if tmptext1 < tmptext2:
                    tmptext1 += wordlist[i]
                    n += 1
                    i += 1
                # elif n > 1:
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
                        # print(i, j, [tokenized_text[j - 1]])
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
                    # print(i, j, [tmptext1], [tmptext2])
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
            # except:
            #     print(wordlist)
            #     print(tokenized_text)
            #     break
        # while (1):
        #     print(i, j, [tmptext1], [tmptext2])
        #     if (tmptext1 == tmptext2 and tmptext1 != ""):
        #         print(i, j, [tmptext1], [tmptext2])
        #         for k in range(n):
        #             matched_infoe.append(tmpinfo / n)
        #             length_factor.append(math.ceil(m / n))
        #         tmptext1 = ""
        #         tmptext2 = ""
        #         tmpinfo = 0
        #         n = 0
        #         m = 0
        #     elif i >= len(wordlist) and j >= len(tokenized_text):
        #         break
        #     elif i >= len(wordlist) or j >= len(tokenized_text):
        #         badlabel = 1
        #         break
        #     elif tmptext1 < tmptext2:
        #         tmptext1 += wordlist[i]
        #         n += 1
        #         i += 1
        #     # elif n > 1:
        #     else:
        #         if tmptext1 == "":
        #             tmptext1 = wordlist[i]
        #             i += 1
        #             n = 1
        #         if re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j]):
        #             length = len(tmptext2)
        #             if tmptext1[0:length] != tmptext2:
        #                 badlabel = 1
        #                 break
        #             utftext = ""
        #             while (1):
        #                 if j >= len(tokenized_text) or (not re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j])):
        #                     badlabel = 1
        #                     j = len(tokenized_text) + 1
        #                     break
        #                 utftext += re.search(r"<0x[A-F0-9][A-F0-9]>", tokenized_text[j]).group()[3:5]
        #                 tmpinfo += infoentropy[j].item()
        #                 m += 1
        #                 j += 1
        #                 try:
        #                     tmp_character = bytes.fromhex(utftext).decode("utf-8")
        #                     if tmp_character == tmptext1[length]:
        #                         tmptext2 += tmp_character
        #                         break
        #                 except BaseException as e:
        #                     pass
        #         else:
        #             tmptext2 += tokenized_text[j]
        #             tmpinfo += infoentropy[j].item()
        #             m += 1
        #             j += 1
        # print(edge)
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
        # print(edge)
    if len(wordlist)!=len(matched_infoe):
        # print(wordlist)
        # print(tokenized_text)
        badlabel=1
    # print(badlabel,endlabel,sentence)
    # print(badlabel,wordlist,tokenized_text)
    # print(infoentropy)
    # print(matched_infoe)
    # print(edge)

    if badlabel:
        print(wordlist)
        print(original_wordlist)
        print(tokenized_text)
        print([sentence])
        # print(endlabel)
    # print(badlabel,wordlist,edge,matched_infoe,length_factor,triple_text,past_key_values,past_sentence)
    # print(wordlist,edge,length_factor,matched_infoe)
    # print("####")
    return badlabel,wordlist,edge,matched_infoe,length_factor,triple_text,past_key_values,past_sentence


# 生成BBPE的字节到Unicode映射（与GPT-2相同）
def bytes_to_unicode():
    bs=list(range(ord("!"),ord("~")+1))+list(range(ord("¡"),ord("¬")+1))+list(range(ord("®"),ord("ÿ")+1))
    cs=bs[:]
    n=0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256+n)
            n+=1
    cs=[chr(n) for n in cs]
    return {b:c for b,c in zip(bs,cs)}


def clean_bbpe_tokens(tokens):
    # 创建逆向映射字典（Unicode字符 → 字节）
    byte_encoder=bytes_to_unicode()
    unicode_to_byte_dict={v:k for k,v in byte_encoder.items()}

    clean_tokens=[]
    is_first_token=True

    for token in tokens:
        # 将token中的字符映射回原始字节
        byte_list=[]
        for char in token:
            byte_val=unicode_to_byte_dict.get(char)
            if byte_val is not None:
                byte_list.append(byte_val)
            else:
                # 处理未知字符（直接取ASCII值）
                byte_list.append(ord(char)%256)
        token_bytes=bytes(byte_list)

        # 检查是否以空格字节(0x20)开头
        has_leading_space=token_bytes.startswith(b' ')
        if has_leading_space:
            token_bytes=token_bytes[1:]  # 移除开头的空格字节

        # 将字节解码为UTF-8字符串，并转义控制字符
        try:
            decoded_str=token_bytes.decode('utf-8')
        except UnicodeDecodeError:
            decoded_str=''.join(f'<0x{b:02X}>' for b in token_bytes)  # 无效UTF-8时按字节转义

        escaped_str=''
        for char in decoded_str:
            code=ord(char)
            if code<32 or code==127:  # 控制字符或DEL
                escaped_str+=f'<0x{code:02X}>'
            else:
                escaped_str+=char

        # 添加▁前缀规则：首标记或包含空格的标记
        if is_first_token or has_leading_space:
            cleaned_token='▁'+escaped_str
        else:
            cleaned_token=escaped_str

        clean_tokens.append(cleaned_token)
        is_first_token=False  # 仅首标记标记一次

    return clean_tokens


if __name__=="__main__":
    # 示例使用
    original_tokens=['for','Ġsale','Ġlast','Ġyear','Ġat','ĠÂ£','1','.','6','5','m','.','Ċ']
    cleaned_tokens=clean_bbpe_tokens(original_tokens)
    print(cleaned_tokens)
    # 输出：['▁for', '▁sale', '▁last', '▁year', '▁at', '▁£', '1', '.', '6', '5', 'm', '.', '<0x0A>']