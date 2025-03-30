from openai import OpenAI

def chat(prompt, system = ""):
    client = OpenAI(
        api_key="IITM-hackday",
        base_url="https://llm-gateway.heurist.xyz"
    )
    
    completion = client.chat.completions.create(
        model="mistralai/mixtral-8x22b-instruct",
        messages=[
            {"role":"system","content":system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    
    response = completion.choices[0].message.content
    
    return response