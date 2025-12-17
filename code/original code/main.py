import os
import sys
import time
import Decoupled_component
import decp23
import decp24
import decp25
import decp26
import General_line

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
    infoentropy_model="llama2-7b-hf",
    sent_simplify_label=True,
    without_tree=False,
    device_map="cuda",
    evaluate_mode="hfp-llama2-70b",
    token_id=0,
    multiprocessing_num=1,
    folder_path="",
    standard_answer=None,
    module_label=["1","2","3"]
):
    # print(module_label)

    # test_label=True
    test_label=False

    if "1" in module_label:
        os.mkdir(folder_path)
        with open(folder_path+"/1.txt","a") as logf:
            original_stdout=sys.stdout

            if not test_label:
                sys.stdout=logf

            if propagation_ratio_list in ["selecting","llmlingua","llmlingua2","longllmlingua"] or propagation_ratio_list[0:5]=="Qwen2":

                print("dataset",dataset)
                print("ratio",ratio)
                print("evaluate_mode",evaluate_mode)
                print("auto_para_label",auto_para_label)
                print("compress_question",compress_question)
                print("baseline "+propagation_ratio_list)

                Decoupled_component.general_line(
                    compress_method=propagation_ratio_list,
                    dataset=dataset,
                    ratio=ratio,
                    auto_para_label=2,
                    compress_question=False,
                    folder_path=folder_path
                )

            else:
                propagation_ratio_list=propagation_ratio_list.split(",")
                propagation_ratio_list=[float(item) for item in propagation_ratio_list]
                print("dataset",dataset)
                print("mode",mode)
                print("ratio",ratio)
                print("auto_para_label",auto_para_label)
                print("compress_question",compress_question)
                print("overall_parse_compress_label",overall_parse_compress_label)
                print("adjust_ratio_list",adjust_ratio_list)
                print("first_word_adjust_label",first_word_adjust_label)
                print("hierarchical_global_label",hierarchical_global_label)
                print("tree_propagation_label",tree_propagation_label)
                print("propagation_ratio_list",propagation_ratio_list)
                print("triple_label",triple_label)
                print("without_infoentropy",without_infoentropy)
                print("infoentropy_model",infoentropy_model)
                print("sent_simplify_label",sent_simplify_label)
                print("without_tree",without_tree)
                print("device_map",device_map)
                print("evaluate_mode",evaluate_mode)
                print("token_id",token_id)
                print("multiprocessing_num",multiprocessing_num)
                print("standard_answer",standard_answer)
                print("module_label",module_label)
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
                    infoentropy_model,
                    sent_simplify_label,
                    without_tree,
                    device_map,
                    folder_path,
                    # standard_answer
                )
            sys.stdout=original_stdout

    if "2" in module_label:
        with open(folder_path+"/2.txt","a") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)
            Decoupled_component.llm_generate_line(
                folder_path,
                standard_answer,
                evaluate_mode,
                multiprocessing_num,
                token_id
            )
            sys.stdout=original_stdout

    if "3" in module_label:
        if dataset[0:5]=="arXiv":
            log_folder_path=folder_path+"/3"+chr(ord(dataset[5])-ord("1")+ord("a"))+".txt"
        else:
            log_folder_path=folder_path+"/3"+".txt"
        with open(log_folder_path,"w") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)
            Decoupled_component.batch_scoring(
                folder_path,
                standard_answer,
                dataset
            )
            sys.stdout=original_stdout

    if "4" in module_label:
        with open(folder_path+"/4.txt","w") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)
            Decoupled_component.batch_prompt_evaluate(
                folder_path,
                dataset
            )
            sys.stdout=original_stdout

    if "5" in module_label:
        with open(folder_path+"/5.txt","w") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)
            Decoupled_component.batch_context_match(
                folder_path
            )
            sys.stdout=original_stdout

    if "6" in module_label:
        with open(folder_path+"/6.txt","w") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)

            decp25.sent_length_value_exp(
                dataset,
                auto_para_label=auto_para_label,
                compress_question=compress_question,
                triple_label=triple_label,
                without_infoentropy=without_infoentropy,
                sent_simplify_label=sent_simplify_label,
                device_map="cuda",
            )
            sys.stdout=original_stdout

    if "7" in module_label:
        with open(folder_path+"/7.txt","w") as logf:
            original_stdout=sys.stdout
            sys.stdout=logf
            print("module_label",module_label)
            decp26.length_eval(folder_path)
            sys.stdout=original_stdout
        if dataset=="LongBench":
            with open(folder_path+"/7score.txt","w") as logf:
                original_stdout=sys.stdout
                sys.stdout=logf
                print("module_label",module_label)

                import metric.LongBenchEval
                metric.LongBenchEval.Eval(folder_path)

                sys.stdout=original_stdout



start_time=time.time()
token_id=sys.argv[1] # 0
ratio=(sys.argv[2]) # 0.1,0.2
propagation_ratio_list=(sys.argv[3]) # 0.95,1,0.6,1,0
folder_path=sys.argv[4] # 0530_1
standard_answer=sys.argv[5]
if standard_answer=="N":
    standard_answer=None
module_label=sys.argv[6] # 1
module_label=[item for item in module_label]
dataset=sys.argv[7]
evaluate_mode=sys.argv[8]

if len(sys.argv)>9:
    infoentropy_model=sys.argv[9]
else:
    infoentropy_model="llama2-7b-hf"

# dataset="BBCnews",
# dataset="GSM8K",
# dataset="arXiv",
# dataset="truncate_arXiv",
# dataset="hotpotQA",

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
    infoentropy_model=infoentropy_model,
    sent_simplify_label=True,
    without_tree=False,
    # device_map="cpu",
    device_map="cuda",
    # evaluate_mode="hfp-llama2-70b",
    # evaluate_mode="hfp-Mixtral-8x7B",
    # evaluate_mode="hfp-llama3-70b",
    evaluate_mode=evaluate_mode,
    token_id=int(token_id),
    multiprocessing_num=10,
    folder_path=folder_path,
    standard_answer=standard_answer,
    module_label=module_label
)
end_time=time.time()
print(f"{end_time-start_time}seconds")