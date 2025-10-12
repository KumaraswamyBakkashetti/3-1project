from ollama import Client

client = Client(host='http://localhost:11434')

def llama_call(prompt):
    response = client.chat(
        model='llama3.1:8b',
        messages=[{'role': 'user', 'content': prompt}],
        stream=False
    )
    return response['message']['content']
