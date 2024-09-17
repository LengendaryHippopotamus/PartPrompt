import os
import sys
import time
import Decoupled_component
def partprompt(
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
    propagation_ratio_list="0.95,1,0.6,1,1",
    triple_label=False,
    without_infoentropy=True,
    sent_simplify_label=True,
    without_tree=False,
    device_map="cuda",
    folder_path="",
):
    os.mkdir(folder_path)
    with open(folder_path+"/1.txt","a") as logf:
        original_stdout=sys.stdout
        sys.stdout=logf
        propagation_ratio_list=propagation_ratio_list.split(",")
        propagation_ratio_list=[float(item) for item in propagation_ratio_list]
        Decoupled_component.hierarchical_prompt(
            dataset,
            mode,
            ratio,
            auto_para_label,
            compress_question,
            overall_parse_compress_label,
            adjust_ratio_list,
            first_word_adjust_label,
            hierarchical_global_label,
            tree_propagation_label,
            propagation_ratio_list,
            triple_label,
            without_infoentropy,
            sent_simplify_label,
            without_tree,
            device_map,
            folder_path,
        )
        sys.stdout=original_stdout

start_time=time.time()
dataset=sys.argv[1]
# dataset="BBCnews",
# dataset="GSM8Koriginal",
# dataset="arXiv",
# dataset="truncate_arXiv",
# dataset="hotpotQA",
ratio=(sys.argv[2]) # 0.2,0.3,0.5
propagation_ratio_list=(sys.argv[3]) # 1.0,1.0,0.7,4.0,0.0,100.0
folder_path=sys.argv[4] # 0530_1
partprompt(
    dataset=dataset,
    mode="tokens",
    ratio=ratio,
    auto_para_label=[0,1,2],
    compress_question=False,
    overall_parse_compress_label=True,
    adjust_ratio_list=[0.0,0.0,0.0,0.0,0.0,0.0],
    first_word_adjust_label=False,
    hierarchical_global_label=True,
    tree_propagation_label=True,
    propagation_ratio_list=propagation_ratio_list,
    triple_label=False,
    without_infoentropy=False,
    sent_simplify_label=True,
    without_tree=False,
    device_map="cuda",
    folder_path=folder_path,
)
end_time=time.time()
print(f"{end_time-start_time}seconds")