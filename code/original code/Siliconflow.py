from openai import OpenAI
def siliconflow_generate(prompt):
    client = OpenAI(api_key="your-key", base_url="https://api.siliconflow.cn/v1")
    response = client.chat.completions.create(
        model='mistralai/Mixtral-8x7B-Instruct-v0.1',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        stream=False,
        max_tokens=300,
        temperature=0
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content


if(__name__=="__main__"):
    prompt="Transformer is"
    output=siliconflow_generate(prompt)
    print(output)