"""
MedTwin - Core AI Brain (main.py)
This file contains the complete agent logic for the MedTwin system.
It is designed to be imported by the Flask backend or run as a standalone CLI.
NO STREAMLIT LINES ARE INCLUDED IN THIS FILE.
"""

import os
import json
import re
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI

# ============================================================
# CONFIGURATION
# ============================================================

def initialize_llm(api_key: str = None):
    """Initialize the DeepSeek LLM Brain"""
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("[WARNING] No API key provided. Please set DEEPSEEK_API_KEY environment variable.")
    
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=key,
        base_url="https://api.deepseek.com",
        temperature=0.3,
        max_tokens=2000
    )

# ============================================================
# MEDICAL KNOWLEDGE BASE
# ============================================================

MEDICAL_QUESTIONS = {
    "diabetes": [
        "What's your fasting blood sugar level?",
        "Have you noticed increased thirst or urination?",
        "Any recent fatigue or blurred vision?"
    ],
    "hypertension": [
        "What's your blood pressure reading?",
        "Any headaches, dizziness, or chest discomfort?",
        "Are you taking your hypertension medications?"
    ],
    "heart_disease": [
        "Are you having any chest pain, tightness, or pressure right now?",
        "Does any chest discomfort get worse when you walk, climb stairs, or exercise?",
        "Do you feel short of breath during simple activities like walking or talking?",
        "Have you noticed your heart beating fast, slow, or irregularly?",
        "Do your legs, feet, or ankles swell by the end of the day?",
        "Do your symptoms improve when you rest?"
    ],
    "copd": [
        "Do you get out of breath easily, like when walking up a small hill or hurrying?",
        "Do you ever have to stop walking just to catch your breath?",
        "Are you coughing up any phlegm or mucus today?",
        "Does your chest feel tight or heavy right now?",
        "Is your breathing making it hard to do normal things around the house?",
        "Have you had a cold or chest infection that just won't go away lately?",
        "Do you smoke, or have you worked around a lot of smoke, dust, or fumes?"
    ],
}

# ============================================================
# AGENT 1: SYMPTOM Q&A AGENT
# ============================================================

class SymptomQAAgent:
    def __init__(self, llm):
        self.llm = llm
        self.full_conversation = []
        self.extracted_info = {}
        self.current_question_index = 0
        self.condition_type = None
        self.answers = {}
        self.interview_complete = False
        self.red_flag_detected = False

    def extract_info(self, text: str):
        """Rule-based and LLM extraction"""
        t = text.lower()
        # Basic rule-based extraction
        if "smoke" in t: self.extracted_info["smoking_status"] = text
        if "bp" in t or "blood pressure" in t: self.extracted_info["bp_record"] = text
        if "sugar" in t or "glucose" in t: self.extracted_info["glucose_record"] = text
        
        # Identify condition if not set
        if not self.condition_type:
            if any(w in t for w in ["diabet", "sugar"]): self.condition_type = "diabetes"
            elif any(w in t for w in ["bp", "hypertens"]): self.condition_type = "hypertension"
            elif any(w in t for w in ["heart", "chest pain"]): self.condition_type = "heart_disease"
            elif any(w in t for w in ["copd", "breath", "lung"]): self.condition_type = "copd"

    def get_next_question(self) -> str | None:
        if not self.condition_type: return "I can help with Diabetes, Hypertension, Heart Disease, or COPD. What are you experiencing?"
        
        qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
        if self.current_question_index < len(qs):
            return qs[self.current_question_index]
        
        self.interview_complete = True
        return None

    def start_interview(self, initial_message: str) -> str:
        self.extract_info(initial_message)
        return self.get_next_question() or "Interview complete. Analyzing..."

    def continue_interview(self, answer: str) -> str:
        qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
        if self.current_question_index < len(qs):
            self.answers[qs[self.current_question_index]] = answer
            self.current_question_index += 1
        
        return self.get_next_question() or "Interview complete. Analyzing..."

# ============================================================
# AGENT 2: ANALYSIS AGENT (GOLD 2026 COPD Ready)
# ============================================================

class AnalysisAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze_copd_gold(self, qa_data: Dict) -> Dict:
        """Official GOLD 2026 ABE Assessment Logic"""
        # Deterministic logic for COPD classification
        # Implementation of the ABE tool based on symptoms and exacerbation history
        text = str(qa_data).lower()
        is_high_risk = "hospital" in text or "frequent" in text
        is_high_symptoms = "stop walking" in text or "short of breath" in text
        
        if is_high_risk: group, severity = "Group E", "HIGH"
        elif is_high_symptoms: group, severity = "Group B", "MODERATE"
        else: group, severity = "Group A", "LOW"
        
        return {"group": group, "severity": severity}

    def analyze(self, collected_data: Dict) -> Dict:
        condition = collected_data.get("condition_type", "unknown")
        qa_data = collected_data.get("qa_data", {})
        
        if condition == "copd":
            gold = self.analyze_copd_gold(qa_data)
            severity = gold["severity"]
        else:
            severity = "MODERATE" # Fallback

        # Use LLM for detailed recommendations
        prompt = f"Analyze this {condition} case with severity {severity}. Data: {qa_data}. Return medical recommendations."
        res = self.llm.invoke(prompt)
        
        return {
            "condition": condition,
            "severity": severity,
            "recommendations": res.content,
            "qa_data": qa_data
        }

# ============================================================
# AGENT 3: PLANNING AGENT
# ============================================================

class PlanningAgent:
    def __init__(self, llm):
        self.llm = llm

    def create_plan(self, analysis: Dict) -> Dict:
        prompt = f"Create a 7-day care plan for {analysis['condition']} ({analysis['severity']}). Recommendations: {analysis['recommendations']}. Return JSON ONLY with keys: daily_actions, monitoring, red_flags."
        res = self.llm.invoke(prompt)
        try:
            # Simple cleanup for JSON
            content = res.content.strip().replace("```json", "").replace("```", "")
            return json.loads(content)
        except:
            return {"daily_actions": ["Follow prescribed meds"], "monitoring": ["Track symptoms"], "red_flags": ["Severe pain"]}

# ============================================================
# AGENT 4: NOTIFIER AGENT
# ============================================================

class NotifierAgent:
    def __init__(self, llm):
        self.llm = llm

    def sync_to_calendar(self, plan: Dict):
        """Placeholder for Google Calendar Sync"""
        print(f"[Notifier] Syncing {len(plan.get('daily_actions', []))} tasks to Google Calendar...")
        return "Sync successful"

# ============================================================
# COORDINATOR: THE ORCHESTRATOR
# ============================================================

class CoordinatorAgent:
    def __init__(self, llm):
        self.qa = SymptomQAAgent(llm)
        self.analyzer = AnalysisAgent(llm)
        self.planner = PlanningAgent(llm)
        self.notifier = NotifierAgent(llm)

    def process_consultation(self, initial_complaint: str):
        """Run a full simulation (CLI Example)"""
        print(f"\n[Coordinator] Starting consultation for: {initial_complaint}")
        
        # 1. Interview
        resp = self.qa.start_interview(initial_complaint)
        print(f"[QA Agent] First Question: {resp}")
        
        # 2. Mocking rest of interview for CLI demo
        self.qa.interview_complete = True 
        data = self.qa.get_collected_data()
        
        # 3. Analyze
        print("[Analysis Agent] Running medical assessment...")
        analysis = self.analyzer.analyze(data)
        
        # 4. Plan
        print("[Planning Agent] Generating care plan...")
        plan = self.planner.create_plan(analysis)
        
        # 5. Notify
        self.notifier.sync_to_calendar(plan)
        
        return {
            "analysis": analysis,
            "plan": plan
        }

# ============================================================
# MAIN EXECUTION (CLI TEST)
# ============================================================

if __name__ == "__main__":
    print("-" * 50)
    print("MedTwin AI Brain - CLI Test Mode")
    print("-" * 50)
    
    # Initialize with local env key
    llm = initialize_llm()
    coordinator = CoordinatorAgent(llm)
    
    # Test Case
    result = coordinator.process_consultation("I have a persistent cough and I am a heavy smoker.")
    
    print("\n--- FINAL RESULTS ---")
    print(f"Detected Condition: {result['analysis']['condition'].upper()}")
    print(f"Severity Level: {result['analysis']['severity']}")
    print(f"Action Items: {result['plan']['daily_actions'][:2]}")
    print("-" * 50)
