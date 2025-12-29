"""
Comprehensive Agent Testing Script
Tests all MedTwin agents to ensure they're working correctly
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("MEDTWIN AGENTS COMPREHENSIVE TEST")
print("=" * 60)
print()

# Test 1: Environment Check
print("TEST 1: Environment Variables")
print("-" * 60)
deepseek_key = os.getenv('DEEPSEEK_API_KEY')
if deepseek_key:
    print(f"[OK] DEEPSEEK_API_KEY found: {deepseek_key[:10]}...")
else:
    print("[ERROR] DEEPSEEK_API_KEY is missing!")
print()

# Test 2: LLM Initialization
print("TEST 2: LLM Initialization")
print("-" * 60)
try:
    from agents import get_llm
    llm = get_llm()
    print(f"[OK] LLM initialized successfully")
    print(f"   Type: {type(llm).__name__}")
except Exception as e:
    print(f"[ERROR] LLM initialization failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 3: SymptomQAAgent
print("TEST 3: SymptomQAAgent")
print("-" * 60)
try:
    from agents import get_symptom_agent
    symptom_agent = get_symptom_agent()
    print(f"[OK] SymptomQAAgent created")
    
    # Test interview start
    response = symptom_agent.start_interview("I have chest pain and shortness of breath")
    print(f"[OK] Interview started")
    print(f"   Condition detected: {symptom_agent.condition_type}")
    print(f"   First question: {response[:100]}...")
    
    # Test continue
    response2 = symptom_agent.continue_interview("Yes, it hurts when I walk")
    print(f"[OK] Interview continued")
    print(f"   Next question: {response2[:100]}...")
    
    # Get collected data
    data = symptom_agent.get_collected_data()
    print(f"[OK] Collected data: {json.dumps(data, indent=2)}")
    
except Exception as e:
    print(f"[ERROR] SymptomQAAgent test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 4: AnalysisAgent
print("TEST 4: AnalysisAgent")
print("-" * 60)
try:
    from agents import get_analysis_agent
    analysis_agent = get_analysis_agent()
    print(f"[OK] AnalysisAgent created")
    
    # Test analysis with sample data
    sample_data = {
        "condition_type": "heart_disease",
        "qa_data": {
            "chest_pain": "yes, during exercise",
            "shortness_of_breath": "yes",
            "swelling": "no"
        }
    }
    
    analysis = analysis_agent.analyze(sample_data)
    print(f"[OK] Analysis completed")
    print(f"   Severity: {analysis.get('severity')}")
    print(f"   Recommendations: {analysis.get('recommendations', '')[:100]}...")
    
except Exception as e:
    print(f"[ERROR] AnalysisAgent test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 5: PlanningAgent
print("TEST 5: PlanningAgent")
print("-" * 60)
try:
    from agents import get_planning_agent
    planning_agent = get_planning_agent()
    print(f"[OK] PlanningAgent created")
    
    # Test with sample analysis result
    sample_analysis = {
        "condition": "heart_disease",
        "severity": "MODERATE",
        "qa_data": {"chest_pain": "yes"}
    }
    
    plan = planning_agent.create_comprehensive_plan(sample_analysis)
    print(f"[OK] Care plan created")
    print(f"   Short-term actions: {len(plan.get('short_term_plan', {}).get('daily_actions', []))}")
    print(f"   Long-term goals: {len(plan.get('long_term_plan', {}).get('goals', []))}")
    
except Exception as e:
    print(f"[ERROR] PlanningAgent test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 6: NotifierAgent
print("TEST 6: NotifierAgent")
print("-" * 60)
try:
    from agents import get_notifier_agent
    notifier_agent = get_notifier_agent()
    print(f"[OK] NotifierAgent created")
    print(f"   Type: {type(notifier_agent).__name__}")
    
except Exception as e:
    print(f"[ERROR] NotifierAgent test failed: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 7: API Endpoints Check
print("TEST 7: API Endpoints Check")
print("-" * 60)
import requests

endpoints = [
    ('GET', 'http://localhost:5000/api/health'),
    ('GET', 'http://localhost:5000/'),
]

for method, url in endpoints:
    try:
        response = requests.request(method, url, timeout=5)
        if response.status_code == 200:
            print(f"[OK] {method} {url} - Status: {response.status_code}")
        else:
            print(f"[WARN] {method} {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] {method} {url} - Error: {e}")
print()

# Test 8: Database Models
print("TEST 8: Database Models")
print("-" * 60)
try:
    from models.consultation import Consultation
    from models.user import User
    from models.medication import Medication
    print(f"[OK] All database models imported successfully")
    print(f"   - User")
    print(f"   - Consultation")
    print(f"   - Medication")
except Exception as e:
    print(f"[ERROR] Database models import failed: {e}")
print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("All critical agents have been tested.")
print("Check the output above for any [ERROR] marks.")
print("=" * 60)
