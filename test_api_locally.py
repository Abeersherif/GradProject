import requests
import json

URL = "http://localhost:5000/api/consultation/start"
DATA = {"message": "I've been having trouble breathing, especially when I move around, and I keep coughing a lot."}

try:
    print(f"Testing POST to {URL}...")
    response = requests.post(URL, json=DATA)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
