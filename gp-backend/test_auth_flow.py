import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_login_and_meds():
    # 1. Login
    print("Logging in...")
    login_payload = {
        "email": "alex@medtwin.com",
        "password": "demo"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        print(f"Login Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(resp.text)
            return
            
        data = resp.json()
        token = data.get("access_token")
        print(f"Token received: {token[:20]}...")
        
        # 2. List Medications
        print("\nFetching medications...")
        headers = {"Authorization": f"Bearer {token}"}
        med_resp = requests.get(f"{BASE_URL}/medications/", headers=headers)
        
        print(f"Meds Status: {med_resp.status_code}")
        print(med_resp.text)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_and_meds()
