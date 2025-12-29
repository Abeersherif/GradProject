import requests

# Test doctor login to get token
login_url = "http://localhost:5000/api/auth/login"
credentials = {
    "email": "ahmedmohamed@gmail.com",
    "password": "12345678"
}

response = requests.post(login_url, json=credentials)
if response.status_code == 200:
    token = response.json()['access_token']
    user_id = response.json()['user']['id']
    print(f"Doctor logged in. ID: {user_id}")
    
    # Now try to get patient history
    # Let's assume patient ID 1 exists (Abeer Sherif)
    patient_id = 1
    history_url = f"http://localhost:5000/api/patient/{patient_id}/consultations"
    headers = {"Authorization": f"Bearer {token}"}
    
    res = requests.get(history_url, headers=headers)
    print(f"History Response Status: {res.status_code}")
    print(f"History Response Body: {res.text[:500]}")
else:
    print(f"Login failed: {response.text}")
