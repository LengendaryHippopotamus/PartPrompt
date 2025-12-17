import json


def RULER_niah_Eval(folder_path):
    answer_path=folder_path+"/standard_answer.json"
    with open(answer_path,'r',encoding='utf-8') as f:
        answers=json.load(f)
    output_path=folder_path+"/llm_output.json"
    with open(output_path,'r',encoding='utf-8') as f:
        outputs=json.load(f)

    length_path=folder_path+"/length.json"
    with open(output_path,'r',encoding='utf-8') as f:
        lengths=json.load(f)

    scores=[[] for x in range(len(outputs[0]))]

    for i in range(len(outputs)):
        # print(i)
        # print(outputs[i])
        answer=answers[i]
        for j,output_item in enumerate(outputs[i]):
            output_text=output_item[1]
            # print(output_text)
            # print(answer)
            score=1.0 if answer[0].lower() in output_text.lower() else 0.0
            scores[j].append(score)
        # break
    # print(scores)
    return scores