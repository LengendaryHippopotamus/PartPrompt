# 2024/3/8 20:27
import time
import random
from metric import hotpot_evaluate,GSM8k_eval
from metric.BERTscore1 import Bert_eval


def local_llm_generate(
    input_prompt,
    tokenizer,
    model,
    mode,
    max_tokens
):
    inputs=tokenizer(input_prompt, return_tensors="pt")
    length = inputs.input_ids.shape[1]
    if mode=="llama2-7b":
        generate_ids = model.generate(inputs.input_ids.cuda(), max_length=length + max_tokens)
        generate_ids = generate_ids[0:1, length:]
        output = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    elif mode=="Qwen2-72B-Instruct":
        from transformers import AutoTokenizer
        model_name="Qwen/Qwen2-72B-Instruct"
        tokenizer=AutoTokenizer.from_pretrained(model_name)
        messages=[
            {"role":"system","content":"You are a helpful assistant."},
            {"role":"user","content":input_prompt}
        ]
        text=tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs=tokenizer([text],return_tensors="pt").to("cuda")
        generated_ids=model.generate(
            model_inputs.input_ids,
            max_new_tokens=max_tokens
        )
        generated_ids=[output_ids[len(input_ids):] for input_ids,output_ids in zip(model_inputs.input_ids,generated_ids)]
        output=tokenizer.batch_decode(generated_ids,skip_special_tokens=True)[0]
    # elif mode=="mixtral_local":
    #     # use Mixtral-8x7B-Instruct-v0.1
    #     from openai import OpenAI
    #     client=OpenAI(base_url="http://localhost:8000/v1",api_key="none")
    #     response=client.chat.completions.create(
    #         model="Mixtral-8x7B-Instruct",
    #         messages=[
    #             {"role":"user","content":input_prompt}
    #         ],
    #         max_tokens=300,
    #         temperature=0
    #     )
    #     output=response.choices[0].message.content
    return length, output

def hfp_llm_generate(
    input_prompt,
    tokenizer,
    mode,
    max_tokens,
    token
):
    inputs=tokenizer(input_prompt, return_tensors="pt")
    length = inputs.input_ids.shape[1]
    from huggingface_hub import InferenceClient
    if mode =="hfp-llama2-7b":
        client = InferenceClient(model="meta-llama/Llama-2-7b-chat-hf", token=token)
    elif mode =="hfp-llama2-13b":
        client = InferenceClient(model="meta-llama/Llama-2-13b-chat-hf", token=token)
    elif mode =="hfp-llama2-70b":
        client = InferenceClient(model="meta-llama/Llama-2-70b-chat-hf", token=token)
    elif mode =="hfp-llama3-70b":
        client = InferenceClient(model="meta-llama/Meta-Llama-3-70B-Instruct", token=token)
    elif mode=="hfp-Mixtral-8x7B":
        client = InferenceClient(model="mistralai/Mixtral-8x7B-Instruct-v0.1", token=token)
    while (1):
        try:
            random_number = random.uniform(0, 1)
            time.sleep(random_number)
            output = client.text_generation(input_prompt, max_new_tokens=max_tokens)
            print("hfp-generate")
            break
        except BaseException as e:
            # pass
            # print(e)
            random_number = random.uniform(0, 3)
            time.sleep(random_number)
    return length, output


def evaluate1(
    # revised_prompt,
    # standard_prompt,
    output_list,
    standard_answer,
    dataset,
    coherence_label=False,
    # tokenizer,
    # model,
    # mode
):

    if dataset in ["BBCnews","truncate_arXiv","hotpotQA","arXiv","PeopleDaily","CodeNet"]:
        standard_length=output_list[-1][0]
        standard_output=output_list[-1][1]
        if dataset in ["hotpotQA"]:
            standard_output=standard_answer
        elif dataset in ["arXiv"] and isinstance(standard_answer,str):
            standard_output=standard_answer
        for outputs in output_list:
            length=outputs[0]
            output=outputs[1]

            if output=="" or standard_output=="":
                print(length,standard_length,0)
                # return
                continue

            metric1 = hotpot_evaluate.eval(output, standard_output)
            metric2 = Bert_eval.eval(output, standard_output)



            import nltk
            hypothesis = output.split(" ")
            reference = standard_output.split(" ")
            BLEUscore = nltk.translate.bleu_score.sentence_bleu([reference], hypothesis)

            # print("2s")

            n_gram_list=[0,0,0,0]
            if coherence_label:
                n_gram_list[0]=nltk.translate.bleu_score.sentence_bleu([reference],hypothesis,weights=(1,0,0,0))
                n_gram_list[1]=nltk.translate.bleu_score.sentence_bleu([reference],hypothesis,weights=(0,1,0,0))
                n_gram_list[2]=nltk.translate.bleu_score.sentence_bleu([reference],hypothesis,weights=(0,0,1,0))
                n_gram_list[3]=nltk.translate.bleu_score.sentence_bleu([reference],hypothesis,weights=(0,0,0,1))

                try:
                    disco_scorer_metirc=discoscore(output,standard_output)
                except:
                    disco_scorer_metirc=[0,0,0,0,0,0]

            from rouge import Rouge
            rouge_scorer = Rouge()
            hypothesis = output
            reference = standard_output
            score = rouge_scorer.get_scores(
                hyps=hypothesis,
                refs=reference,
            )

            print(length,standard_length,
                  metric1,
                  BLEUscore,
                  score[0]["rouge-1"]["f"],score[0]["rouge-2"]["f"],score[0]["rouge-l"]["f"],
                  metric2,
                  n_gram_list if coherence_label else "",
                  disco_scorer_metirc if coherence_label else "")

        print("####")
        return

    elif dataset=="GSM8K":
        standard_length=output_list[-1][0]
        standard_output=output_list[-1][1]
        for outputs in output_list:
            length=outputs[0]
            output=outputs[1]
            output = output.split("\n\n")[0]
            # standard_length = tokenizer(standard_prompt, return_tensors="pt").input_ids.shape[1]
            matrix1 = GSM8k_eval.gsm8k_eval(output, standard_answer)
            print(length,standard_length,
                  # disco_scorer_metirc,
                  matrix1)
        print("####")
        return


def discoscore(
        system,
        references
):
    from metric.DiscoScore1.scorer import DiscoScorer
    # system=[
    #     "position near the frontline city of Bakhmut, eastern Ukraine, last week\n\nMore than a dozen European Union member states have agreed to supply Ukraine with at least one million artillery shells over the next year.\n\nThe plan, worth \u20ac2bn in total, was agreed in Brussels on Monday.\n\nUkraine had told the EU it needed 350,000 shells a month to hold back advancing Russian troops and launch a counter-offensive this year.\n\nUkrainian Foreign Minister Dmytro Kuleba hailed the \"game-changing decision\" from the EU.\n\n\"Exactly what is needed,\" he wrote on Twitter. \"Urgent delivery and sustainable joint procurement.\"\n\nThe deal comes as Russia grows concerned at a Ukrainian counter-offensive near Bakhmut or in southern Ukraine, according to a report from think tank Institute for the Study of War.\n\nMeanwhile, Russia's own new year offensive \"may be nearing culmination\", the ISW added.\n\nDefence and foreign ministers from 17 EU countries and Norway signed the ammunition agreement.\n\nThe first part of the plan commits \u20ac1bn ($1.06bn; \u00a3863m) of shared funding for EU states to draw upon their existing stockpiles, with the hope of sending this to Ukraine by the end of May.\n\nThe second part of the deal would see a further \u20ac1bn used to jointly order 155mm shells for Ukraine - the most sought-after artillery rounds.\n\nThe EU is hoping this joint order will incentivise European defence firms to increase their output, with the hope that contracts can be signed by the start of September.\n\nThe deal means each country will have to share details of their ammunition stockpiles - something normally kept secret.\n\nCurrent ammunition production in Europe is said to be lagging behind the levels Ukraine insists it needs to fight Russia.\n\nThere are also questions about how much EU countries can share from their own stockpiles without leaving themselves vulnerable.\n\n\"Increasing industrial capacity is essential,\" EU internal market commissioner Thierry Breton said during a visit to French arms industry company Nexter on Monday.\n\nEU foreign policy chief Josep Borrell recently warned that the bloc had to supply the artillery shells Ukraine needed, or face the prospect of Ukraine losing the war with Russia.\n\nHe said Russian forces were firing about 50,000 rounds of artillery each day and that Ukraine's supplies must be lifted to the same level.\n\nHungary, which has not sent ammunition to Ukraine and has often threatened to veto sanctions against Russia, abstained from Monday's vote in Brussels but foreign minister Peter Szijjarto said it would \"not prevent others from doing what they want\".\n\nNorway also announced on Monday that it had delivered eight German-made Leopard II tanks to Ukraine to be used in a possible Ukrainian counter-offensive against Russia this spring.\n\nSeparately, the US is authorising another $350m in military aid for Ukraine, Secretary of State Antony Blinken said. It includes ammunition for Himars missile launchers, 155mm shells, and howitzer cannon.\n\nLargest donors of military aid to Ukraine by country."]
    # references=[[
    #                 "Members of Ukraine's Armed Forces 80th Separate Air Assault Brigade at their position near the frontline city of Bakhmut, eastern Ukraine, last week\n\nMore than a dozen European Union member states have agreed to supply Ukraine with at least one million artillery shells over the next year.\n\nThe plan, worth \u20ac2bn in total, was agreed in Brussels on Monday.\n\nUkraine had told the EU it needed 350,000 shells a month to hold back advancing Russian troops and launch a counter-offensive this year.\n\nUkrainian Foreign Minister Dmytro Kuleba hailed the \"game-changing decision\" from the EU.\n\n\"Exactly what is needed,\" he wrote on Twitter. \"Urgent delivery and sustainable joint procurement.\"\n\nThe deal comes as Russia grows concerned at a Ukrainian counter-offensive near Bakhmut or in southern Ukraine, according to a report from think tank Institute for the Study of War.\n\nMeanwhile, Russia's own new year offensive \"may be nearing culmination\", the ISW added.\n\nDefence and foreign ministers from 17 EU countries and Norway signed the ammunition agreement.\n\nThe first part of the plan commits \u20ac1bn ($1.06bn; \u00a3863m) of shared funding for EU states to draw upon their existing stockpiles, with the hope of sending this to Ukraine by the end of May.\n\nThe second part of the deal would see a further \u20ac1bn used to jointly order 155mm shells for Ukraine - the most sought-after artillery rounds.\n\nThe EU is hoping this joint order will incentivise European defence firms to increase their output, with the hope that contracts can be signed by the start of September.\n\nThe deal means each country will have to share details of their ammunition stockpiles - something normally kept secret.\n\nCurrent ammunition production in Europe is said to be lagging behind the levels Ukraine insists it needs to fight Russia.\n\nThere are also questions about how much EU countries can share from their own stockpiles without leaving themselves vulnerable.\n\n\"Increasing industrial capacity is essential,\" EU internal market commissioner Thierry Breton said during a visit to French arms industry company Nexter on Monday.\n\nEU foreign policy chief Josep Borrell recently warned that the bloc had to supply the artillery shells Ukraine needed, or face the prospect of Ukraine losing the war with Russia.\n\nHe said Russian forces were firing about 50,000 rounds of artillery each day and that Ukraine's supplies must be lifted to the same level.\n\nHungary, which has not sent ammunition to Ukraine and has often threatened to veto sanctions against Russia, abstained from Monday's vote in Brussels but foreign minister Peter Szijjarto said it would \"not prevent others from doing what they want\".\n\nNorway also announced on Monday that it had delivered eight German-made Leopard II tanks to Ukraine to be used in a possible Ukrainian counter-offensive against Russia this spring.\n\nSeparately, the US is authorising another $350m in military aid for Ukraine, Secretary of State Antony Blinken said. It includes ammunition for Himars missile launchers, 155mm shells, and howitzer cannon.\n\nLargest donors of military aid to Ukraine by country."]]
    disco_scorer=DiscoScorer(
        # device='cuda:0',
        model_name='bert-base-uncased',
        device="cpu",
    )
    disco_scorer_metirc=[]
    for s,refs in zip([system],[[references]]):
        s=s.lower()
        refs=[r.lower() for r in refs]
        disco_scorer_metirc.append(disco_scorer.EntityGraph(s,refs))
        disco_scorer_metirc.append(disco_scorer.LexicalChain(s,refs))
        disco_scorer_metirc.append(disco_scorer.RC(s,refs))
        disco_scorer_metirc.append(disco_scorer.LC(s,refs))
        disco_scorer_metirc.append(disco_scorer.DS_Focus_NN(s,refs))  # FocusDiff
        disco_scorer_metirc.append(disco_scorer.DS_SENT_NN(s,refs))  # SentGraph
    # print(disco_scorer_metirc)
    return disco_scorer_metirc