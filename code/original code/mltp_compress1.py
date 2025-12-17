# merge(list1,list2)
# solution_propagation
# solution_list
# schedule
# while(1):
    # schedule
    #     上传
    # solution_list筛查
    #     分线程合并
    # 读取合并进度写入
# import Infotree
# from Infotree import infotree
import copy
from concurrent.futures import ThreadPoolExecutor,as_completed
import time
def merge_solution(i,a,b,P,Q):
    m=len(P)-1
    n=len(Q)-1
    S=[]
    for k in range(0,m+n+1):
    # for k in range(u,v):
        infol=0
        label=0
        for l in range(max(0,k-n),min(m,k)+1):
            if(P[l][0]+Q[k-l][0]>infol):
                infol=P[l][0]+Q[k-l][0]
                label=l
        S.append([infol]+P[label][1:]+Q[k-label][1:])
    # print("P",P)
    # print("Q",Q)
    # print("S",S)
    return (i,a,b,S)

def solution_propagation1(
    self,
    process_num
):
    length=len(self.edge[0])+1
    # schedule=copy.deepcopy(self.sonode)
    schedule=[]
    # print(self.sonode)
    for item in self.sonode:
        # print(item)
        schedule.append(len(item))
    solution_list=[]
    for i in range(length):
        solution_list.append([[[0]]])
    # print(length,len(schedule),len(solution_list),len(self.sonode))

    edge1,edge2=self.edge[0],self.edge[1]
    edge1,edge2=zip(*sorted(zip(edge1,edge2),key=lambda pair:pair[1]))
    self.edge=[[0]+list(edge1),[0]+list(edge2)]

    with ThreadPoolExecutor(max_workers=process_num) as executor:
        futures=[]
        # idex=0
        while(1):
            # print(len(futures))
            # print(schedule)
            # for i,nodes in enumerate(schedule):
            #     if nodes==[]:
            # for idx in range(length):
            #     print(idx,solution_list[idx])
            for i,num in enumerate(schedule):
                if num==0:
                    headlist=[]
                    S=solution_list[i][0]
                    for j in range(self.length_factor[i]):
                        headlist.append([0])
                    for item in S:
                        item[0]+=self.infoentropy[i]
                        item.append(i)
                    solution_list[i][0]=headlist+S
                    solution_list[self.edge[0][i]].append(solution_list[i][0])
                    # for idx in range(length):
                    #     print(idx,solution_list[idx])
                    schedule[i]-=1
                    # schedule[self.edge[0][i]].remove(i)
                    # schedule[self.edge[0][i]]-=1
            # print(0)
            # for i,solutions in enumerate(solution_list):
            #     while(len(solutions)>1):
            #         print(i,len(solutions),solutions)
            #         # S=merge_solution(solutions[0],solutions[1])
            #         # solution_list[i]=S+solutions[2:]
            #         a=0
            #         b=1
            #         future=executor.submit(merge_solution,i,a,b,solutions[0],solutions[1])
            #         futures.append(future)
            #         solution_list[i]=solutions[2:]
            #         solutions=solutions[2:]
            #         print(i,len(solutions),solutions)


            for i in range(len(solution_list)):
                while(len(solution_list[i])>1):
                    # print(i,len(solution_list[i]),solution_list[i])
                    a=0
                    b=1
                    future=executor.submit(merge_solution,i,a,b,solution_list[i][0],solution_list[i][1])
                    futures.append(future)
                    solution_list[i]=solution_list[i][2:]
                    # print(i,len(solution_list[i]),solution_list[i])

            new_futures=[]
            # print(1)
            for future in futures:
                if future.done():
                    ret=future.result()
                    # print(ret)
                    solution_list[ret[0]].append(ret[3])
                    # print("ret",ret[3])
                    schedule[ret[0]]-=1
                else:
                    new_futures.append(future)
            futures=new_futures

            # for i in range(len(solution_list)):
            #     while (len(solution_list[i])>1):
            #         # print(i,len(solution_list[i]),solution_list[i])
            #         a=0
            #         b=1
            #         ret=merge_solution(i,a,b,solution_list[i][0],solution_list[i][1])
            #         # print("ret",ret[3])
            #         solution_list[i]=solution_list[i][2:]
            #         solution_list[ret[0]].append(ret[3])
            #         # print(i,len(solution_list[i]),solution_list[i])
            #         schedule[ret[0]]-=1
            #         # print(schedule)
            #         # for idx in range(length):
            #         #     print(idx,solution_list[idx])

            # if schedule[0]==[]:
            # print(2)
            if schedule[0]==0:
                break
            # idex+=1
    return solution_list[0][0]

# infotree.solution_propagation1=solution_propagation1


