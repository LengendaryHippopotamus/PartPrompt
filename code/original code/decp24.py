import sys
import os
import multiprocessing
import tempfile
import shutil

def chunkify(lst,n):# 辅助函数：分割列表为n份
    chunk_size=(len(lst)+n-1)//n  # 向上取整
    return [lst[i:i+chunk_size] for i in range(0,len(lst),chunk_size)]

def worker_process(task_chunk,gpu_id,temp_file_path,dataset):# 工作进程函数
    os.environ["CUDA_VISIBLE_DEVICES"]=str(gpu_id)    # 设置当前进程使用的GPU
    original_stdout=sys.stdout # 本地重定向输出到临时文件
    with open(temp_file_path,'w') as f:
        sys.stdout=f
        for output_list,standard_answer in task_chunk:
            # 注意：这里需确保Evaluate模块在函数内导入（避免GPU冲突）
            import Evaluate  # 替换your_module为实际模块名
            Evaluate.evaluate1(output_list,standard_answer,dataset)
        sys.stdout=original_stdout

def distributed_eval(output_lists,answer_lists,dataset):
    tasks=list(zip(output_lists,answer_lists)) # 准备任务数据
    temp_dir=tempfile.mkdtemp() # 创建临时目录
    try:
        task_chunks=chunkify(tasks,30)     # 分割任务为30份
        processes=[]    # 创建并启动进程
        for i,chunk in enumerate(task_chunks):
            if not chunk:  # 跳过空块
                continue
            gpu_id=i//10         # 分配GPU (0-9 -> GPU0, 10-19 -> GPU1, 20-29 -> GPU2)
            temp_file=os.path.join(temp_dir,f"output_{i}.tmp")         # 临时文件路径
            p=multiprocessing.Process(
                target=worker_process,
                args=(chunk,gpu_id,temp_file,dataset)
            )
            p.start()
            processes.append((i,p,temp_file))

        # 等待所有进程完成
        for idx,p,temp_file in processes:
            p.join()

        # 按顺序合并输出文件
        for i in range(len(task_chunks)):
            temp_file=os.path.join(temp_dir,f"output_{i}.tmp")
            if os.path.exists(temp_file):
                with open(temp_file,'r') as f:
                    print(f.read(),end='',flush=True)  # 保持原样输出
    finally:
        shutil.rmtree(temp_dir)     # 清理临时文件

