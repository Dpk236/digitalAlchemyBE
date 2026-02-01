import ollama

response = ollama.chat(
    model='qwen2.5:7b',
    messages=[{'role': 'user', 'content': 'Explain virtual environments in one sentence'}]
)

print(response['message']['content'])
