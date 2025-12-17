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
import  math

def merge_solution(i,j,a,b,P,Q,m,n,u,v):
    # m=len(P)-1
    # n=len(Q)-1
    S=[]
    # for k in range(0,m+n+1):
    # print("m",m,n,u,v,P,Q,"m")
    for k in range(u,v):
        infol=0
        label=0
        for l in range(max(0,k-n),min(m,k)+1):
            # print(l)
            if (P[l][0]+Q[k-l][0]>=infol):
                infol=P[l][0]+Q[k-l][0]
                label=l
        # print("k",k,label,"k")
        S.append([infol]+P[label][1:]+Q[k-label][1:])
    # time.sleep(1)
    return (i,j,a,b,S)

def num_calculate(m,n,x):
    if x<n:
        return (x+1)*(x+2)/2
    elif x<m:
        return (n+2)*(n+1)/2+(x-n)*(n+1)
    else:
        return m*n+m+n+1-(m+n-x+1)*(m+n-x)/2

def solution_propagation2(
    self,
    process_num,
    block_size
):
    # print(process_num,type(process_num))
    length=len(self.edge[0])+1
    # schedule=copy.deepcopy(self.sonode)
    schedule=[]
    schedule2=[]
    # print(self.sonode)
    for item in self.sonode:
        schedule.append(len(item))
        schedule2.append(0)
    solution_list=[]
    for i in range(length):
        solution_list.append([[[0]]])
    solution_part=[[[] for j in range(len(self.sonode[i]))] for i in range(length)]
    edge1,edge2=self.edge[0],self.edge[1]
    edge1,edge2=zip(*sorted(zip(edge1,edge2),key=lambda pair:pair[1]))
    self.edge=[[0]+list(edge1),[0]+list(edge2)]
    with ThreadPoolExecutor(max_workers=process_num) as executor:
        futures=[]
        # idex=0
        while (1):
            # print(schedule)
            # print(schedule2)
            # for idx in range(length):
            #     print(idx,solution_list[idx])
            # print(solution_part)
            # for i,nodes in enumerate(schedule):
            #     if nodes==[]:
            for i,num in enumerate(schedule):
                if num==0:
                    # print(i)
                    # for idx in range(length):
                    #     print(idx,solution_list[idx])
                    headlist=[]
                    S=solution_list[i][0]
                    for j in range(self.length_factor[i]):
                        headlist.append([0])
                    for item in S:
                        item[0]+=self.infoentropy[i]
                        item.append(i)
                    solution_list[i][0]=headlist+S
                    solution_list[self.edge[0][i]].append(solution_list[i][0])
                    schedule[i]-=1
                    # if(self.edge[0][i]==1):
                    #     print(i)
                        # print("")
                    # schedule[self.edge[0][i]].remove(i)
                    # schedule[self.edge[0][i]]-=1
                    # for idx in range(length):
                    #     print(idx,solution_list[idx])
                    # print("")
            # for i,solutions in enumerate(solution_list):
            #     while (len(solutions)>1):
            #         # S=merge_solution(solutions[0],solutions[1])
            #         # solution_list[i]=S+solutions[2:]
            #         P=solutions[0]
            #         Q=solutions[1]
            #         m=len(P)-1
            #         n=len(Q)-1
            #         if m<n:
            #             m,n=n,m
            #             P,Q=Q,P
            #         num_list=[num_calculate(m,n,x) for x in range(m+n+1)]
            #         b=math.ceil(m*n/block_size)
            #         j=schedule2[i]
            #         v=0
            #         for a in range(1,b+1):
            #             u=v
            #             while(num_list[v]<a*block_size and v<m+n+1):
            #                 v+=1
            #             future=executor.submit(merge_solution,i,j,a,b,P,Q,m,n,u,v)
            #             futures.append(future)
            #         schedule2[i]+=1
            #         solution_list[i]=solutions[2:]
            for i in range(len(solution_list)):
                while (len(solution_list[i])>1):
                    P=solution_list[i][0]
                    Q=solution_list[i][1]
                    m=len(P)-1
                    n=len(Q)-1
                    if m<n:
                        m,n=n,m
                        P,Q=Q,P
                    num_list=[num_calculate(m,n,x) for x in range(m+n+1)]
                    b=math.ceil((m+1)*(n+1)/block_size)
                    j=schedule2[i]
                    v=0
                    # print(m,n,num_list,b)
                    # if i==1 :
                    #     print("P",P)
                    #     print("Q",Q)
                    for a in range(1,b+1):
                        u=v
                        while(v<m+n+1 and num_list[v]<a*block_size):
                            v+=1
                        # print(a,b,u,v)
                        future=executor.submit(merge_solution,i,j,a,b,P,Q,m,n,u,v)
                        futures.append(future)
                        # time.sleep(1)
                        # print(future)
                    schedule2[i]+=1
                    solution_list[i]=solution_list[i][2:]
                    # for idx in range(length):
                    #     print(idx,solution_list[idx])
                    # print("")
            new_futures=[]
            # print(futures)
            for future in futures:
                # print(future)
                if future.done():
                    ret=future.result()
                    # solution_list[ret[0]].append(ret[3])
                    # schedule[ret[0]]-=1
                    # if (ret[0]==1):
                        # print("ret",ret)
                        # print(solution_part)
                    if solution_part[ret[0]][ret[1]]==[]:
                        solution_part[ret[0]][ret[1]].append(ret[3])
                    solution_part[ret[0]][ret[1]].append([ret[2],ret[4]])
                    if len(solution_part[ret[0]][ret[1]])==solution_part[ret[0]][ret[1]][0]+1:
                        tepsolution=[]
                        for item in sorted(solution_part[ret[0]][ret[1]][1:],key=lambda x:x[0]):
                            # if (ret[0]==1):
                            #     print("i",item[1:])
                            # tepsolution+=item[1:]
                            tepsolution+=item[1]
                        # print("part",solution_list[ret[0]])
                        # print(tepsolution)
                        solution_list[ret[0]].append(tepsolution)
                        # print("s",solution_list[ret[0]])
                        # print(tepsolution)
                        # solution_list[ret[0]]+=tepsolution
                        schedule[ret[0]]-=1
                        solution_part[ret[0]][ret[1]]=0
                else:
                    new_futures.append(future)
            futures=new_futures
            # print(futures)
            # if schedule[0]==[]:
            if schedule[0]==0:
                break
            # idex+=1
    return solution_list[0][0]

# infotree.solution_propagation2=solution_propagation2
