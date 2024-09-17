def edge_process(
    wordlist,
    edge,
    infoentropy,
    length_factor,
    global_parse_compress_label,
    endlabel_list,
    hierarchical_global_label
):
    length_list = [0]
    length = len(edge)
    if global_parse_compress_label:
        for i in range(length):
            length_list.append(len(wordlist[i]))
            length_list[i+1]+=length_list[i]
        allwordlist=[[]]
        alledge=[[[],[]]]
        allinfoentropy=[[]]
        alllength_factor=[[]]
        for i in range(length):
            allwordlist[0]+=wordlist[i]
            allinfoentropy[0]+=infoentropy[i]
            alllength_factor[0]+=length_factor[i]
            alledge[0][0] += [item + length_list[i] for item in edge[i][0]]
            alledge[0][1] += [item + length_list[i] for item in edge[i][1]]
            alledge[0][0][length_list[i]]=0
        allwordlist[0].insert(0, "")
        allinfoentropy[0].insert(0, 0)
        alllength_factor[0].insert(0, 0)
        if hierarchical_global_label==True:
            endlabel_list[-1]=2
            last_node=len(alledge[0][0])+len(endlabel_list)+sum(endlabel_list)
            node_id=[0,0,0,0]
            hierarchical_edge_list=[[[],[]],[[],[]],[[],[]]]
            for i in range(len(endlabel_list)).__reversed__():
                for j in range(endlabel_list[i]+1).__reversed__():
                    # last_node+=1
                    node_id[j]=last_node
                    last_node-=1
                    allwordlist[0].append("")
                    allinfoentropy[0].append(0)
                    alllength_factor[0].append(0)
                    hierarchical_edge_list[j][0].append(node_id[j+1])
                    hierarchical_edge_list[j][1].append(node_id[j])
                alledge[0][0][length_list[i]]=node_id[0]
            for edge_list in hierarchical_edge_list:
                alledge[0][0]+=edge_list[0]
                alledge[0][1]+=edge_list[1]
        return allwordlist,alledge,allinfoentropy,alllength_factor
    else:
        for i in range(length):
            wordlist[i].insert(0,"")
            infoentropy[i].insert(0,0)
            length_factor[i].insert(0,0)
        return wordlist, edge, infoentropy, length_factor
if(__name__=="__main__"):
    wordlist=[['Members', 'of', 'Ukraine', "'s", 'Armed', 'Forces', '80th', 'Separate', 'Air', 'Assault', 'Brigade', 'at', 'their', 'position', 'near', 'the', 'frontline', 'city', 'of', 'Bakhmut', ',', 'eastern', 'Ukraine', ',', 'last', 'week'], ['More', 'than', 'a', 'dozen', 'European', 'Union', 'member', 'states', 'have', 'agreed', 'to', 'supply', 'Ukraine', 'with', 'at', 'least', 'one', 'million', 'artillery', 'shells', 'over', 'the', 'next', 'year', '.'], ['The', 'plan', ',', 'worth', '€', '2bn', 'in', 'total', ',', 'was', 'agreed', 'in', 'Brussels', 'on', 'Monday', '.']]
    edge=[[[0, 1, 1, 11, 11, 11, 11, 11, 11, 3, 6, 10, 14, 14, 14, 14, 14, 14, 14, 18, 18, 18, 18, 20, 23, 26], [1, 11, 14, 2, 3, 6, 10, 7, 8, 4, 5, 9, 12, 13, 18, 21, 24, 23, 26, 15, 16, 17, 20, 19, 22, 25]], [[0, 1, 4, 4, 8, 8, 6, 7, 10, 10, 10, 10, 12, 12, 12, 12, 20, 20, 20, 16, 18, 18, 24, 24, 24], [10, 2, 1, 3, 4, 7, 5, 6, 8, 9, 12, 25, 11, 13, 20, 24, 14, 18, 19, 15, 16, 17, 21, 22, 23]], [[0, 2, 2, 2, 2, 11, 11, 11, 11, 11, 4, 4, 5, 8, 13, 15], [11, 1, 3, 9, 4, 2, 10, 13, 15, 16, 5, 8, 6, 7, 12, 14]]]
    infoentropy=[[9.226356029510498, 0.535660982131958, 8.52357292175293, 1.093097580363974, 4.757957685738802, 0.024137793108820915, 12.064543336629868, 2.0558740582782775, 1.495116114616394, 1.4980343434144743, 0.11701386421918869, 5.74370002746582, 2.7735488414764404, 2.5461971759796143, 1.3041799068450928, 0.9898878335952759, 2.955255091190338, 4.38525390625, 0.012067525647580624, 2.662125070608454, 0.7359819412231445, 3.283513307571411, 0.016023319214582443, 0.354085773229599, 5.685155868530273, 1.0296344757080078], [6.637740135192871, 1.4328151941299438, 2.329371690750122, 2.2935996055603027, 6.70106315612793, 2.847588062286377, 2.184257984161377, 0.15284650027751923, 0.9774320125579834, 3.034212350845337, 0.30589595437049866, 6.545153617858887, 1.468556523323059, 0.04188248887658119, 5.627467155456543, 0.0040144105441868305, 2.9379475116729736, 0.47351258993148804, 1.273794039618224, 0.1376943543436937, 2.919273614883423, 0.09332100301980972, 0.2133222222328186, 2.199817657470703, 2.217323064804077], [3.16508412361145, 8.507692337036133, 3.408895254135132, 7.7706170082092285, 3.3002986907958984, 5.6335742473602295, 3.2613284587860107, 0.7312160134315491, 0.13137337565422058, 2.478278160095215, 3.1190807819366455, 2.191685914993286, 3.2991154739866033, 1.0784170627593994, 1.7835869789123535, 1.733694076538086]]
    length_factor=[[2, 1, 1, 2, 2, 1, 4, 3, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1]]
    edge_process(
        wordlist,
        edge,
        infoentropy,
        length_factor,
        global_parse_compress_label=True,
        endlabel_list=[0,1,2],
        hierarchical_global_label=True
    )