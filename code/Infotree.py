import torch
import copy
import math
class infotree:
    def __init__(self,
                 infoentropy,
                 edge,
                 length_factor,
                 without_infoentropy,
                 propagation_ratio_list,
                 text=None,
                 without_tree=False,
                 ):
        self.infoentropy=infoentropy
        self.edge=edge
        self.length_factor=length_factor
        self.without_infoentropy=without_infoentropy
        self.text=text
        self.sonode=[]
        self.propagation_ratio_list=propagation_ratio_list
        self.without_tree=without_tree

    def construct(self):
        length=len(self.edge[0])
        for i in range(length+1):
            self.sonode.append([])
        for i in range(length):
            if self.edge[0][i]>=0:
                self.sonode[self.edge[0][i]].append(self.edge[1][i])
        for i in range(length+1):
            self.sonode[i]=sorted(self.sonode[i])
        return

    def tree_plot(self):
        log = self.tree_recurf("",0,"")
        print(log)
        print("####")
        return

    def tree_recurf(self,log,i,n):
        if log!="":
            log+="\n"
        log+=n
        log+=str(i)
        log+=" "
        log+=str(round(self.infoentropy[i],6))
        if self.text!=None:
            log+="\t"
            if self.text[i]=="":
                log+="\"\""
            elif self.text[i]=="\n":
                log+="\\n"
            else:
                log+=self.text[i]
        if self.sonode[i]!=[]:
            for item in sorted(self.sonode[i]):
                log=self.tree_recurf(log,item,n+"\t")
        return log

    def rootward_propagation(self):
        self.rootward_recurf(0)
        return

    def rootward_recurf(self,i):
        momentum_list=[]
        for j in self.sonode[i]:
            momentum_list.append(self.rootward_recurf(j))
        momentum=self.rootward_update(momentum_list,i)
        return momentum

    def rootward_update(self,momentum_list,i):
        ret=sum([math.pow(item,self.propagation_ratio_list[0]) for item in momentum_list])
        if self.infoentropy[i]==0 and self.length_factor[i]==0:
            ret/=len(momentum_list)
            self.infoentropy[i]=ret
        else:
            ret+=self.infoentropy[i]
            ret/=(len(momentum_list)+1)
        return ret

    def leafward_propagation(self):
        self.infoentropy[0]=1
        momentum1=1
        momentum2=1
        self.leafward_recurf(0,momentum1,momentum2)
        return

    def leafward_recurf(self,i,momentum1,momentum2):
        momentum1,momentum2=self.leafward_update(momentum1,momentum2,i)
        for j in self.sonode[i]:
            if j==self.sonode[i][0] and self.length_factor[i]==0:
                self.leafward_recurf(j,momentum1*self.propagation_ratio_list[5],momentum2)
            else:
                self.leafward_recurf(j,momentum1,momentum2)

    def leafward_update(self,momentum1,momentum2,i):
        if self.propagation_ratio_list[4]>=0:
            tmpmomentum=(math.pow(momentum1,self.propagation_ratio_list[3])
                         *math.pow(momentum2,self.propagation_ratio_list[4]))
        else:
            tmpmomentum=(math.pow(momentum1,self.propagation_ratio_list[3])
                         *math.pow(momentum2/100,self.propagation_ratio_list[4]))
        if self.length_factor[i]==0:
            momentum1=math.pow(momentum1,self.propagation_ratio_list[1])
            momentum1*=self.infoentropy[i]
        momentum2=math.pow(momentum2,self.propagation_ratio_list[2])
        momentum2*=self.infoentropy[i]
        self.infoentropy[i]*=tmpmomentum
        return momentum1,momentum2


    def compress_recurf(self,i):
        if self.sonode[i]==[]:
            ret=[[0]]
        elif(len(self.sonode[i])==1):
            ret=self.compress_recurf(self.sonode[i][0])
        else:
            ret=[[0]]
            for j in self.sonode[i]:
                len1=len(ret)-1
                sonlist=self.compress_recurf(j)
                len2=len(sonlist)-1
                tmp=[]
                for k in range(0,len1+len2+1):
                    infol=0
                    label=0
                    for l in range(max(0,k-len2),min(len1,k)+1):
                        if(ret[l][0]+sonlist[k-l][0]>infol):
                            infol=ret[l][0]+sonlist[k-l][0]
                            label=l
                    tmp.append([infol]+ret[label][1:]+sonlist[k-label][1:])
                ret=tmp
        headlist=[]
        for j in range(self.length_factor[i]):
            headlist.append([0])
        for item in ret:
            item[0]+=self.infoentropy[i]
            item.append(i)
        headlist+=ret
        return headlist


    def compressline(self):
        if self.without_infoentropy:
            node_list=[0]
            i=0
            while(i<len(node_list)):
                node_list+=sorted(self.sonode[node_list[i]])
                i+=1
            infosum=0
            lengthsum=0
            golden_compress=[]
            total_length=sum(self.length_factor)
            i=0
            for j in range(total_length+1):
                while(i<len(node_list)):
                    if lengthsum+self.length_factor[i]<=j:
                        lengthsum+=self.length_factor[i]
                        infosum+=self.infoentropy[i]
                        i+=1
                    else:
                        break
                golden_compress.append([infosum]+node_list[0:i])
        else:
            if self.without_tree==True:
                for i in range(1,len(self.sonode)):
                    self.sonode[0]+=self.sonode[i]
                    self.sonode[i]=[]
            golden_compress = self.compress_recurf(0)
        return golden_compress

if(__name__=="__main__"):
    infoentropy=[0, 9.226356029510498, 0.535660982131958, 8.52357292175293, 1.093097580363974, 4.757957685738802, 0.024137793108820915, 12.064543336629868, 2.0558740582782775, 1.495116114616394, 1.4980343434144743, 0.11701386421918869, 5.74370002746582, 2.7735488414764404, 2.5461971759796143, 1.3041799068450928, 0.9898878335952759, 2.955255091190338, 4.38525390625, 0.012067525647580624, 2.662125070608454, 0.7359819412231445, 3.283513307571411, 0.016023319214582443, 0.354085773229599, 5.685155868530273, 1.0296344757080078, 6.637740135192871, 1.4328151941299438, 2.329371690750122, 2.2935996055603027, 6.70106315612793, 2.847588062286377, 2.184257984161377, 0.15284650027751923, 0.9774320125579834, 3.034212350845337, 0.30589595437049866, 6.545153617858887, 1.468556523323059, 0.04188248887658119, 5.627467155456543, 0.0040144105441868305, 2.9379475116729736, 0.47351258993148804, 1.273794039618224, 0.1376943543436937, 2.919273614883423, 0.09332100301980972, 0.2133222222328186, 2.199817657470703, 2.217323064804077, 3.16508412361145, 8.507692337036133, 3.408895254135132, 7.7706170082092285, 3.3002986907958984, 5.6335742473602295, 3.2613284587860107, 0.7312160134315491, 0.13137337565422058, 2.478278160095215, 3.1190807819366455, 2.191685914993286, 3.2991154739866033, 1.0784170627593994, 1.7835869789123535, 1.733694076538086]
    edge=[[0, 1, 1, 11, 11, 11, 11, 11, 11, 3, 6, 10, 14, 14, 14, 14, 14, 14, 14, 18, 18, 18, 18, 20, 23, 26, 0, 27, 30, 30, 34, 34, 32, 33, 36, 36, 36, 36, 38, 38, 38, 38, 46, 46, 46, 42, 44, 44, 50, 50, 50, 0, 53, 53, 53, 53, 62, 62, 62, 62, 62, 55, 55, 56, 59, 64, 66], [1, 11, 14, 2, 3, 6, 10, 7, 8, 4, 5, 9, 12, 13, 18, 21, 24, 23, 26, 15, 16, 17, 20, 19, 22, 25, 36, 28, 27, 29, 30, 33, 31, 32, 34, 35, 38, 51, 37, 39, 46, 50, 40, 44, 45, 41, 42, 43, 47, 48, 49, 62, 52, 54, 60, 55, 53, 61, 64, 66, 67, 56, 59, 57, 58, 63, 65]]
    length_factor=[0, 2, 1, 1, 2, 2, 1, 4, 3, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1]

    infomation_tree=infotree(
        infoentropy,
        edge,
        length_factor,
        without_infoentropy=False,
        propagation_ratio_list=[0.95,1,0.6,1,1],
        text=None,
        without_tree=True
    )
    infomation_tree.construct()
    print(infomation_tree.sonode)
    infomation_tree.compressline()