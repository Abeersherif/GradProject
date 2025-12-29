import requests
import json

api_key = "sk-cd0246dd1e83434dbfa576d3b7bda641"
url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "say 'Key is Active'"}
    ]
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()['choices'][0]['message']['content']}")
except Exception as e:
    print(f"FAILED: {e}")
