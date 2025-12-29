import requests
import json

api_key = "sk-9281fc022631d4fb483c45a4bf4e9e4e7"
url = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Hi"}
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
