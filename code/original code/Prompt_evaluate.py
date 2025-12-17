import Evaluate
def prompt_evaluate(
        prompt_list,
        tokenizer,
        standard_answer,
        dataset
):
    evaluate_list=[(len(tokenizer.tokenize(prompt)),prompt) for prompt in prompt_list]
    Evaluate.evaluate1(
        evaluate_list,
        standard_answer,
        dataset,
        coherence_label=True
    )

