import requests
import json

# Test starting a consultation
url = "http://localhost:5000/api/consultation/start"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"  # Dummy token for now
}
payload = {
    "message": "i feel that i can't take my breath and i cough almost 3 months ago"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    try:
        print(f"Response text: {response.text}")
    except:
        pass
