from ollama import Client

client = Client(host='https://k7xc1qwz-11434.inc1.devtunnels.ms/')
def llama_call(prompt):
    response = client.chat(
        model='llama3.1:8b',
        messages=[{'role': 'user', 'content': prompt}],
        stream=False
    )
    return response['message']['content']
print(llama_call("HIII"))