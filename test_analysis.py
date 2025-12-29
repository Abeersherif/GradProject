import requests
import json

CONSULTATION_ID = 25 
URL = f"http://localhost:5000/api/consultation/{CONSULTATION_ID}/analyze"

try:
    print(f"Testing POST to {URL} (Waiting up to 60s)...")
    response = requests.post(URL, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Connection failed: {e}")
