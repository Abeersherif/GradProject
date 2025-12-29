"""
COMPREHENSIVE SYSTEM VERIFICATION
Tests all components: Backend, Database, Agents, and API endpoints
"""
import os
import sys
import json
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*70)
print(" MEDTWIN COMPLETE SYSTEM VERIFICATION")
print("="*70 + "\n")

# PART 1: ENVIRONMENT & CONFIGURATION
print("PART 1: ENVIRONMENT CHECK")
print("-"*70)

api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key:
    print(f"[OK] DEEPSEEK_API_KEY is set: {api_key[:12]}...")
else:
    print("[ERROR] DEEPSEEK_API_KEY not found!")

port = os.getenv('PORT', '5000')
print(f"[OK] Backend port: {port}")
print()

# PART 2: DATABASE VERIFICATION
print("PART 2: DATABASE VERIFICATION")
print("-"*70)

try:
    from database import db
    from models.user import User
    from models.consultation import Consultation
    from models.medication import Medication
    from models.ticket import Ticket
    print("[OK] All database models loaded")
    print("   - User")
    print("   - Consultation")
    print("   - Medication")
    print("   - Ticket")
except Exception as e:
    print(f"[ERROR] Database import failed: {e}")

print()

# PART 3: AGENT VERIFICATION
print("PART 3: AGENT SYSTEM VERIFICATION")
print("-"*70)

try:
    from agents import get_llm, get_symptom_agent, get_analysis_agent
    from agents import get_planning_agent, get_notifier_agent
    
    # Test LLM
    llm = get_llm()
    print(f"[OK] LLM initialized: {type(llm).__name__}")
    
    # Test SymptomQAAgent
    symptom_agent = get_symptom_agent()
    test_response = symptom_agent.start_interview("I have chest pain and shortness of breath")
    print(f"[OK] SymptomQAAgent working")
    print(f"   - Detected condition: {symptom_agent.condition_type}")
    print(f"   - Interview active: {not symptom_agent.interview_complete}")
    
    # Test AnalysisAgent
    analysis_agent = get_analysis_agent()
    test_analysis = analysis_agent.analyze({
        "condition_type": "heart_disease",
        "qa_data": {"chest_pain": "yes", "shortness_of_breath": "yes"}
    })
    print(f"[OK] AnalysisAgent working")
    print(f"   - Test severity: {test_analysis.get('severity')}")
    
    # Test PlanningAgent
    planning_agent = get_planning_agent()
    test_plan = planning_agent.create_comprehensive_plan({
        "condition": "heart_disease",
        "severity": "MODERATE",
        "qa_data": {}
    })
    print(f"[OK] PlanningAgent working")
    print(f"   - Generated plan with {len(test_plan.get('short_term_plan', {}).get('daily_actions', []))} daily actions")
    
    # Test NotifierAgent
    notifier_agent = get_notifier_agent()
    print(f"[OK] NotifierAgent initialized")
    
except Exception as e:
    print(f"[ERROR] Agent verification failed: {e}")
    import traceback
    traceback.print_exc()

print()

# PART 4: API ENDPOINT VERIFICATION
print("PART 4: API ENDPOINT VERIFICATION")
print("-"*70)

import requests

endpoints_to_test = [
    ("GET", "http://localhost:5000/api/health", "Health Check"),
    ("GET", "http://localhost:5000/", "Root Endpoint"),
    ("GET", "http://localhost:5000/api/consultation/list", "List Consultations"),
]

for method, url, description in endpoints_to_test:
    try:
        r = requests.request(method, url, timeout=3)
        if r.status_code == 200:
            print(f"[OK] {description} - {r.status_code}")
        else:
            print(f"[WARN] {description} - {r.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] {description} - Backend not responding")
    except Exception as e:
        print(f"[ERROR] {description} - {str(e)[:40]}")

print()

# PART 5: WORKFLOW TEST (End-to-End)
print("PART 5: END-TO-END WORKFLOW TEST")
print("-"*70)

try:
    # Step 1: Start consultation
    r1 = requests.post(
        "http://localhost:5000/api/consultation/start",
        json={"message": "I have chest pain and difficulty breathing"},
        timeout=10
    )
    if r1.status_code == 201:
        data1 = r1.json()
        consultation_id = data1.get('consultationId')
        print(f"[OK] Step 1: Consultation started (ID: {consultation_id})")
        
        # Step 2: Continue consultation
        r2 = requests.post(
            f"http://localhost:5000/api/consultation/{consultation_id}/continue",
            json={"message": "Yes, it gets worse when I walk"},
            timeout=10
        )
        if r2.status_code == 200:
            print(f"[OK] Step 2: Consultation continued")
            
            # Continue until completed
            completed = r2.json().get('completed', False)
            iteration = 3
            while not completed and iteration <= 7:
                r_continue = requests.post(
                    f"http://localhost:5000/api/consultation/{consultation_id}/continue",
                    json={"message": "No"},
                    timeout=10
                )
                completed = r_continue.json().get('completed', False)
                print(f"[OK] Step {iteration}: Interview iteration {iteration-2}")
                iteration += 1
            
            if completed:
                print(f"[OK] Step {iteration}: Interview completed")
                
                # Step 3: Analyze
                r3 = requests.post(
                    f"http://localhost:5000/api/consultation/{consultation_id}/analyze",
                    timeout=15
                )
                if r3.status_code == 200:
                    analysis = r3.json().get('analysis', {})
                    print(f"[OK] Step {iteration+1}: Analysis completed")
                    print(f"   - Severity: {analysis.get('severity')}")
                    
                    # Step 4: Generate plan
                    r4 = requests.post(
                        f"http://localhost:5000/api/consultation/{consultation_id}/plan",
                        timeout=15
                    )
                    if r4.status_code == 200:
                        plan = r4.json().get('plan', {})
                        print(f"[OK] Step {iteration+2}: Care plan generated")
                        print(f"   - Daily actions: {len(plan.get('short_term_plan', {}).get('daily_actions', []))}")
                        print(f"[OK] FULL WORKFLOW COMPLETED SUCCESSFULLY!")
                    else:
                        print(f"[ERROR] Step {iteration+2}: Plan generation failed - {r4.status_code}")
                else:
                    print(f"[ERROR] Step {iteration+1}: Analysis failed - {r3.status_code}")
        else:
            print(f"[ERROR] Step 2: Continuation failed - {r2.status_code}")
    else:
        print(f"[ERROR] Step 1: Start failed - {r1.status_code}")
        
except Exception as e:
    print(f"[ERROR] Workflow test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# FINAL SUMMARY
print("="*70)
print(" VERIFICATION SUMMARY")
print("="*70)
print("System verification complete. Check above for [ERROR] marks.")
print("If you see mostly [OK], your system is working correctly!")
print("="*70 + "\n")
