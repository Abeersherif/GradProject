"""Quick agent validation"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*60)
print("AGENT STATUS CHECK")
print("="*60 + "\n")

# 1. Check API Key
key = os.getenv('DEEPSEEK_API_KEY')
if key:
    print(f"1. API Key: [OK] {key[:10]}...")
else:
    print("1. API Key: [ERROR] Not found")

# 2. Test LLM
try:
    from agents import get_llm
    llm = get_llm()
    print(f"2. LLM Init: [OK] {type(llm).__name__}")
except Exception as e:
    print(f"2. LLM Init: [ERROR] {str(e)[:50]}")

# 3. Test Symptom Agent
try:
    from agents import get_symptom_agent
    agent = get_symptom_agent()
    resp = agent.start_interview("I have chest pain")
    print(f"3. SymptomQA: [OK] Detected: {agent.condition_type}")
except Exception as e:
    print(f"3. SymptomQA: [ERROR] {str(e)[:50]}")

# 4. Test Analysis Agent
try:
    from agents import get_analysis_agent
    agent = get_analysis_agent()
    result = agent.analyze({"condition_type": "copd", "qa_data": {"smoking": "yes"}})
    print(f"4. Analysis: [OK] Severity: {result.get('severity')}")
except Exception as e:
    print(f"4. Analysis: [ERROR] {str(e)[:50]}")

# 5. Test Planning Agent
try:
    from agents import get_planning_agent
    agent = get_planning_agent()
    plan = agent.create_comprehensive_plan({"condition": "copd", "severity": "MODERATE", "qa_data": {}})
    print(f"5. Planning: [OK] Generated plan")
except Exception as e:
    print(f"5. Planning: [ERROR] {str(e)[:50]}")

# 6. Test Notifier Agent
try:
    from agents import get_notifier_agent
    agent = get_notifier_agent()
    print(f"6. Notifier: [OK] Created")
except Exception as e:
    print(f"6. Notifier: [ERROR] {str(e)[:50]}")

# 7. Check API
try:
    import requests
    r = requests.get('http://localhost:5000/api/health', timeout=2)
    print(f"7. Backend: [OK] {r.status_code}")
except Exception as e:
    print(f"7. Backend: [ERROR] Not responding")

print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60 + "\n")
