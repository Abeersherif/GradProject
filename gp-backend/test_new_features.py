"""
Test CSV Export and Coordinator Agent
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

print("\n" + "="*70)
print("TESTING CSV EXPORT & COORDINATOR AGENT")
print("="*70 + "\n")

# Test 1: Doctor Queue (triggers Coordinator Agent)
print("TEST 1: Doctor Queue with Coordinator Agent")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/doctor/queue", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"[OK] Doctor queue retrieved")
        print(f"   Total tickets: {data.get('total', 0)}")
        if data.get('queue'):
            for ticket in data['queue'][:2]:  # Show first 2
                print(f"   - Ticket #{ticket['ticket_id']}: {ticket['patient']['name']}")
                print(f"     Priority: {ticket['priority_score']} | Status: {ticket['status']}")
    else:
        print(f"[ERROR] Status: {r.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# Test 2: Doctor Dashboard
print("TEST 2: Doctor Dashboard")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/doctor/dashboard", timeout=5)
    if r.status_code == 200:
        data = r.json()
        stats = data.get('statistics', {})
        print(f"[OK] Dashboard loaded")
        print(f"   Pending reviews: {stats.get('pending_reviews', 0)}")
        print(f"   Total patients: {stats.get('total_patients', 0)}")
    else:
        print(f"[ERROR] Status: {r.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# Test 3: Patient Export
print("TEST 3: Patient Data Export")
print("-"*70)
try:
    r = requests.get(f"{BASE_URL}/patient/export-data", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f"[OK] Export successful")
        print(f"   Message: {data.get('message')}")
        print(f"   Download URL: {data.get('download_url')}")
    else:
        print(f"[ERROR] Status: {r.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# Test 4: Coordinator Agent Directly
print("TEST 4: Coordinator Agent (Direct)")
print("-"*70)
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from agents import get_coordinator_agent
    
    agent = get_coordinator_agent()
    print(f"[OK] Coordinator Agent created: {type(agent).__name__}")
    
    # Test with sample data
    sample_consultation = {
        'id': 999,
        'patient_id': 1,
        'created_at': '2025-12-28T00:00:00',
        'analysis_result': {
            'condition': 'heart_disease',
            'severity': 'MODERATE',
            'recommendations': 'Monitor closely',
            'reasoning': 'Test data'
        },
        'care_plan': {
            'short_term_plan': {
                'daily_actions': ['Test action'],
                'monitoring': ['Test monitoring']
            }
        },
        'collected_data': {
            'condition_type': 'heart_disease',
            'qa_data': {'chest_pain': 'yes'}
        },
        'conversation_history': []
    }
    
    ticket = agent.create_medical_ticket(sample_consultation)
    print(f"[OK] Medical ticket created")
    print(f"   Ticket ID: {ticket.get('ticket_id')}")
    print(f"   Priority: {ticket.get('priority_score')}")
    print(f"   Status: {ticket.get('status')}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("ALL TESTS COMPLETED")
print("="*70 + "\n")
