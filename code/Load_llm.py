import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
def load_llm(model_path,load_model_label=True,device_map="cuda"):
    model_config = {}
    trust_remote_code = model_config.get("trust_remote_code", True)
    if "trust_remote_code" not in model_config:
        model_config["trust_remote_code"] = trust_remote_code
    config = AutoConfig.from_pretrained(
        model_path, trust_remote_code=trust_remote_code
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, trust_remote_code=trust_remote_code
    )
    if model_config.get("pad_to_left", True):
        tokenizer.padding_side = "left"
        tokenizer.pad_token_id = (
            config.pad_token_id if config.pad_token_id else tokenizer.eos_token_id
        )
    if load_model_label:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype="auto" if device_map == "cuda" else torch.float32,
            device_map=device_map,
            config=config,
            ignore_mismatched_sizes=True,
            **model_config,
        )
    else:
        model=None
    context_idxs = []
    max_position_embeddings = config.max_position_embeddings
    return model,tokenizer,context_idxs,max_position_embeddings,device_map

