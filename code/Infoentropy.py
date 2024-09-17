import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
def get_ppl(
        past_length,
        model,
        input_ids=None,
        attention_mask=None,
        past_key_values=None,
        end=None,
):
    past_length=0
    with torch.no_grad():
        response = model(
            input_ids[:, past_length:end],
            attention_mask=attention_mask[:, :end],
            past_key_values=past_key_values,
            use_cache=True,
        )
        past_key_values = response.past_key_values
    shift_logits = response.logits[..., :-1, :].contiguous()
    shift_labels = input_ids[..., past_length + 1: end].contiguous()
    active = (attention_mask[:, past_length:end] == 1)[..., :-1].view(-1)
    active_logits = shift_logits.view(-1, shift_logits.size(-1))[active]
    active_labels = shift_labels.view(-1)[active]
    loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
    loss = loss_fct(active_logits, active_labels)
    return loss,past_key_values

def infoentropy(
        text: str,
        triple_text: str,
        tokenizer,
        device,
        max_position_embeddings,
        model,
        input_ids=None,
        attention_mask=None,
        past_key_values=None,
        past_sentence=None,
        return_kv=True,
        end=None,
        condition_mode: str = "none",
        condition_pos_id: int = 0
):
    originlen = len(tokenizer.tokenize(text))

    if past_sentence!="":
        past_length = len(tokenizer.tokenize(past_sentence))
        if past_sentence[-1]!="\n" and text[0]!=" ":
            text=past_sentence+" "+text
        else:
            text=past_sentence+text
        triple_text=""
    else:
        past_length = 0
    if triple_text != "":
        if text[0] != " ":
            triple_text += " "
        text = triple_text + text
    tokenized_text = tokenizer(text, return_tensors="pt")
    input_ids = tokenized_text["input_ids"].to(device)
    attention_mask = tokenized_text["attention_mask"].to(device)

    if end is None:
        end = input_ids.shape[1]

    end = min(end, past_length + max_position_embeddings)
    (loss,past_key_values)=get_ppl(
        past_length,
        model,
        input_ids=input_ids,
        attention_mask=attention_mask,
        past_key_values=None,
        end=None
        )
    return loss[(len(tokenizer.tokenize(text))-originlen):],past_key_values,text