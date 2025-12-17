from transformers import AutoModelForCausalLM, AutoTokenizer

def Qwen_load(model_name):
    model=AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer=AutoTokenizer.from_pretrained(model_name)
    return model,tokenizer

def Qwen_generate_local(
    model,
    tokenizer,
    prompt,
    max_new_tokens
):
    # prompt = "Give me a short introduction to large language model."
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    device="cuda"  # the device to load the model onto
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=max_new_tokens
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # print(response)
    return response

def Qwen_generate_cloud(
    prompt
):
    from openai import OpenAI
    client=OpenAI(
        api_key="your-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    try:
        completion=client.chat.completions.create(
            model='qwen2-72b-instruct',
            messages=[
                {'role':'system','content':'You are a helpful assistant.'},
                {'role':'user','content':prompt}],
            temperature=0,
            top_p=0.8
        )
        print("Qwen_generate")
        return completion.choices[0].message.content

    except:
        completion=""
        print("Qwen_generate_error")
        return completion



