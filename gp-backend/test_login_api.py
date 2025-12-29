import requests
import json

url = "http://localhost:5000/api/auth/login"
payload = {
    "email": "ahmedmohamed@gmail.com",
    "password": "12345678"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
