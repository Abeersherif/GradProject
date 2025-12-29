"""
MedTwin - Medical Assistant Agent System
Powered by DeepSeek AI

This module contains the core agent logic for the MedTwin medical assistant.
"""

import os
import json
import re
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI


# ============================================================
# CONFIGURATION
# ============================================================

def initialize_deepseek(api_key: str = None):
    """
    Initialize DeepSeek LLM with LangChain
    
    Args:
        api_key: DeepSeek API key (if None, reads from environment)
    
    Returns:
        ChatOpenAI instance
    """
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0.3,
        max_tokens=2000
    )
    
    return llm


# ============================================================
# MEDICAL QUESTIONS DATABASE
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
        "",
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
# HELPER FUNCTIONS
# ============================================================

def contains_root(text: str, roots: List[str]) -> bool:
    """
    Check if any root/keyword appears in text (case-insensitive)
    
    Args:
        text: Text to search
        roots: List of root keywords
    
    Returns:
        True if any root is found
    """
    text_lower = text.lower()
    return any(root in text_lower for root in roots)


def parse_llm_output(llm_response: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse LLM JSON output
    
    Args:
        llm_response: Raw LLM response
    
    Returns:
        Parsed dictionary or empty dict on failure
    """
    try:
        # Clean markdown code blocks if present
        content = llm_response.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        data = json.loads(content)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


# ============================================================
# AGENT 1: SYMPTOM Q&A AGENT
# ============================================================

class SymptomQAAgent:
    """
    Medical interview agent that conducts Q&A sessions with patients
    and extracts relevant medical information.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.full_conversation: List[str] = []
        self.extracted_info: Dict[str, Any] = {}
        self.current_question_index: int = 0
        self.condition_type: str | None = None
        self.answers: Dict[str, str] = {}
        self.interview_complete: bool = False
        self.red_flag_detected: bool = False
        self.awaiting_disambiguation: bool = False
        self.possible_conditions: List[str] = []

    def rule_based_extract(self, text: str):
        """Extract medical information using rule-based patterns"""
        text_lower = text.lower()

        # Timing
        if re.search(r"\bfor (\d+) (day|week|hour)s?\b", text_lower):
            self.extracted_info["timing"] = text

        if any(p in text_lower for p in [
            "days ago", "day ago", "weeks ago", "week ago",
            "last night", "yesterday", "this morning", "hours ago", "since"
        ]):
            self.extracted_info["timing"] = text

        # Severity
        if re.search(r'(\d{1,2})\s*/\s*10', text_lower) or \
           re.search(r'\b(mild|moderate|severe|unbearable)\b', text_lower):
            self.extracted_info["severity"] = text

        # Glucose
        if re.search(r'\bglucose\b|\bblood sugar\b|\bmg/dl\b|\bmmol\b', text_lower):
            self.extracted_info["glucose"] = text

        # Blood pressure
        if re.search(r'\b(bp|blood pressure)\b|\bmmhg\b|\d+/\d+', text_lower):
            self.extracted_info["blood_pressure"] = text

        # Medication
        if re.search(r'\b(medication|meds|pills|tablets|taking|took|missed|forgot)\b', text_lower):
            self.extracted_info["medication"] = text

        # Breathing
        if any(k in text_lower for k in [
            "shortness of breath", "can't breathe", "cannot breathe", "struggling to breathe",
            "difficulty breathing", "hard to breathe", "breathless", "dyspnea"
        ]) or re.search(r'\bbreath(ing)?\b', text_lower):
            self.extracted_info["breathing_status"] = text

        # Red flags
        if any(r in text_lower for r in [
            "can't breathe", "cannot breathe", "struggling to breathe",
            "severe chest pain", "crushing chest pain",
            "blue lips", "blue face", "passed out", "fainted"
        ]):
            self.extracted_info["red_flag"] = text
            self.red_flag_detected = True

    def llm_synonym_extract(self, text: str):
        """Extract symptoms using LLM for better understanding"""
        prompt = (
            "Extract all symptoms, medical concepts, and possible intent from this message.\n"
            "Return JSON ONLY with this structure:\n"
            "{\n"
            '  "symptom1": {\n'
            '    "Canonical": "...",\n'
            '    "Original": "...",\n'
            '    "Corrected": "...",\n'
            '    "Synonyms": ["..."],\n'
            '    "Intent": "..."\n'
            "  }\n"
            "}\n"
            f'Message: "{text}"'
        )
        raw = self.llm.invoke(prompt).content.strip()
        llm_data = parse_llm_output(raw)

        for key, data in llm_data.items():
            if isinstance(data, dict):
                self.extracted_info[key] = {
                    "canonical": data.get("Canonical", ""),
                    "original": data.get("Original", ""),
                    "corrected": data.get("Corrected", ""),
                    "synonyms": data.get("Synonyms", []),
                    "intent": data.get("Intent", "")
                }

    def extract_info_from_text(self, text: str):
        """Extract information using both rule-based and LLM methods"""
        self.rule_based_extract(text)
        self.llm_synonym_extract(text)

    def llm_condition_guess(self, text: str) -> str | None:
        """Use LLM to guess the medical condition"""
        prompt = (
            "Classify the main condition in this message into exactly ONE of:\n"
            "diabetes, hypertension, heart_disease, copd, none.\n"
            'Return ONLY JSON: {"condition": "...", "reason": "..."}\n\n'
            f'Message: "{text}"'
        )
        raw = self.llm.invoke(prompt).content.strip()

        try:
            data = json.loads(raw)
            cond = data.get("condition", "none")
            allowed = {"diabetes", "hypertension", "heart_disease", "copd"}
            return cond if cond in allowed else None
        except Exception:
            return None

    def identify_condition(self, patient_input: str) -> str | None:
        """Identify the medical condition from patient input"""
        patient_lower = patient_input.lower()

        synonym_parts: List[str] = []
        for key, value in self.extracted_info.items():
            if isinstance(value, dict):
                synonym_parts.append(value.get("canonical", ""))
                synonym_parts.append(value.get("corrected", ""))
                synonym_parts.append(value.get("intent", ""))
                syns = value.get("synonyms", [])
                if isinstance(syns, list):
                    synonym_parts.extend(syns)
                else:
                    synonym_parts.append(str(syns))

        combined_text = (patient_lower + " " + " ".join(synonym_parts)).lower()

        # Check for specific conditions
        has_diabetes = contains_root(combined_text, ["diabet", "glucose", "blood sugar"])
        has_hypertension = contains_root(combined_text, ["blood pressure", "hypertens", "bp"])

        has_heart = contains_root(
            combined_text,
            [
                "heart", "cardiac",
                "chest pain", "chest tightness", "chest discomfort",
                "angina", "pain when walking", "pain when exercising",
                "shortness of breath on activity",
                "heart rate", "palpitations", "fatigue on exertion",
                "electric pumping"
            ]
        )

        has_copd_core = contains_root(
            combined_text,
            ["copd", "chronic obstructive", "emphysema", "chronic bronchitis"]
        )
        has_copd_symptoms = contains_root(combined_text, ["breath"]) and \
                            contains_root(combined_text, ["mucus", "phlegm", "sputum"])

        smoking_and_breath = (
            contains_root(combined_text, ["smok", "cigarette"]) and
            contains_root(combined_text, ["breath", "gasp", "out of breath", "short of breath"])
        )

        has_copd = has_copd_core or has_copd_symptoms or smoking_and_breath

        # Priority: diabetes
        if has_diabetes and not (has_hypertension or has_heart or has_copd):
            self.condition_type = "diabetes"
            return self.condition_type

        # Priority: hypertension
        if has_hypertension and not (has_diabetes or has_heart or has_copd):
            self.condition_type = "hypertension"
            return self.condition_type

        # HEART vs COPD ambiguity
        if has_heart and has_copd and not (has_diabetes or has_hypertension):
            self.condition_type = None
            self.awaiting_disambiguation = True
            self.possible_conditions = ["heart_disease", "copd"]
            return None

        # Unambiguous heart
        if has_heart and not has_copd:
            self.condition_type = "heart_disease"
            return self.condition_type

        # Unambiguous COPD
        if has_copd and not has_heart:
            self.condition_type = "copd"
            return self.condition_type

        # Fallback: LLM guess
        self.condition_type = self.llm_condition_guess(patient_input)
        return self.condition_type

    def get_disambiguation_question(self) -> str:
        """Get question to disambiguate between heart disease and COPD"""
        return (
            "Your symptoms could be related to your heart or to a chronic lung condition.\n"
            "Please answer in your own words, or choose one option:\n\n"
            "A) I feel abnormal heart activity such as electric pumping, weird or fast heart beats, "
            "or a tight band feeling in my upper chest, but I do NOT have heavy mucus or phlegm.\n\n"
            "B) I have a long-lasting cough with thick or heavy mucus or phlegm, especially when I smoke, "
            "or when I am around dust, fumes, or pollution."
        )

    def handle_disambiguation_answer(self, answer: str) -> str | None:
        """Handle patient's answer to disambiguation question"""
        text = answer.lower()

        heart_indicators = [
            "electric pump", "electric pumping",
            "weird heart beat", "weird heartbeat",
            "fast heart beat", "fast heartbeat",
            "irregular heart beat", "irregular heartbeat",
            "palpitations"
        ]

        copd_indicators = [
            "heavy mucus", "thick mucus", "a lot of mucus",
            "mucus", "phlegm", "cough with mucus", "coughing mucus"
        ]

        heart_hit = any(ind in text for ind in heart_indicators)
        copd_hit = any(ind in text for ind in copd_indicators)

        if heart_hit and not copd_hit:
            return "heart_disease"
        if copd_hit and not heart_hit:
            return "copd"

        if re.search(r"\b(a)\b", text) and not re.search(r"\b(b)\b", text):
            return "heart_disease"
        if re.search(r"\b(b)\b", text) and not re.search(r"\b(a)\b", text):
            return "copd"

        return None

    def should_skip_question(self, question: str) -> bool:
        """Check if a question should be skipped based on extracted info"""
        q = question.lower()
        if "glucose" in q and "glucose" in self.extracted_info:
            return True
        if "blood pressure" in q and "blood_pressure" in self.extracted_info:
            return True
        if "med" in q and "medication" in self.extracted_info:
            return True
        return False

    def get_next_question(self) -> str | None:
        """Get the next question in the interview"""
        if not self.condition_type:
            self.interview_complete = True
            return None

        qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
        while self.current_question_index < len(qs):
            q = qs[self.current_question_index]
            if self.should_skip_question(q):
                self.current_question_index += 1
                continue
            return q

        self.interview_complete = True
        return None

    def chat(self, user_message: str, next_question: str | None = None) -> str:
        """Process a chat message and return response"""
        self.full_conversation.append(f"Patient: {user_message}")
        self.extract_info_from_text(user_message)

        if next_question:
            response_text = next_question
        else:
            response_text = "Thank you. I've collected your answers and will analyze them now."

        self.full_conversation.append(f"Agent: {response_text}")
        return response_text

    def start_interview(self, initial_message: str) -> str:
        """Start the medical interview"""
        self.extract_info_from_text(initial_message)
        self.identify_condition(initial_message)

        if self.awaiting_disambiguation and self.possible_conditions == ["heart_disease", "copd"]:
            question = self.get_disambiguation_question()
            self.full_conversation.append(f"Patient: {initial_message}")
            self.full_conversation.append(f"Agent: {question}")
            return question

        if not self.condition_type:
            self.interview_complete = True
            return "Sorry, I can only assist with diabetes, hypertension, heart disease, or COPD."

        self.current_question_index = 0
        first_q = self.get_next_question()
        return self.chat(initial_message, first_q)

    def continue_interview(self, patient_response: str) -> str:
        """Continue the medical interview"""
        if self.awaiting_disambiguation and self.possible_conditions == ["heart_disease", "copd"]:
            chosen = self.handle_disambiguation_answer(patient_response)

            if not chosen:
                guess = self.llm_condition_guess(patient_response)
                if guess in ["heart_disease", "copd"]:
                    chosen = guess
                else:
                    chosen = "heart_disease"

            self.condition_type = chosen
            self.awaiting_disambiguation = False
            self.current_question_index = 0

            next_q = self.get_next_question()
            return self.chat(patient_response, next_q)

        if self.condition_type:
            qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
            if 0 <= self.current_question_index < len(qs):
                prev_q = qs[self.current_question_index]
                self.answers[prev_q] = patient_response

        self.current_question_index += 1
        next_q = self.get_next_question()
        return self.chat(patient_response, next_q)

    def get_collected_data(self) -> Dict[str, Any]:
        """Get all collected data from the interview"""
        return {
            "condition_type": self.condition_type,
            "interview_complete": self.interview_complete,
            "qa_data": {**self.answers, **self.extracted_info},
            "full_conversation": self.full_conversation,
        }


# ============================================================
# AGENT 2: ANALYSIS AGENT
# ============================================================

class AnalysisAgent:
    """
    Medical analysis agent that evaluates patient data and provides
    recommendations. For COPD, it uses the official GOLD 2026 ABE Assessment Tool.
    """
    
    def __init__(self, llm):
        self.llm = llm

    def estimate_severity(self, qa_data: Dict) -> str:
        """Estimate severity of patient's condition"""
        return self._estimate_severity_llm(qa_data)

    def _estimate_severity_llm(self, qa_data: Dict) -> str:
        """Use LLM to estimate severity"""
        prompt = (
            "You are a medical AI. Based on this patient data, classify severity as:\n"
            "LOW, MODERATE, HIGH, or CRITICAL.\n\n"
            "Return ONLY the severity level (one word).\n\n"
            f"Patient Data: {qa_data}"
        )
        response = self.llm.invoke(prompt)
        severity = response.content.strip().upper()

        valid = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        return severity if severity in valid else "MODERATE"

    def analyze_gold_copd(self, qa_data: Dict) -> Dict[str, str]:
        """
        Perform deterministic analysis based on GOLD 2026 Guidelines (ABE Tool).
        Classifies patient into Group A, B, or E.
        """
        # 1. Extract Key Answers from the simplified questions
        # We look for keywords in the *questions* to identify which answer is which
        # because the keys in qa_data are the full question strings.
        
        answers = {k.lower(): v.lower() for k, v in qa_data.items() if isinstance(v, str)}
        
        stop_for_breath = "no"
        infections = "no"
        hospitalized = "no" # Inferred from open text
        
        for q, a in answers.items():
            if "stop walking" in q or "catch your breath" in q:
                stop_for_breath = a
            if "cold or chest infection" in q:
                infections = a
            # Check for hospitalization mentions in any answer
            if "hospital" in a or "admitted" in a or "emergency" in a:
                hospitalized = "yes"

        # 2. Determine Exacerbation Risk (History)
        # GOLD 2026: >= 2 moderate OR >= 1 leading to hospitalization -> Group E
        is_high_risk = False
        if "yes" in infections and ("many" in infections or "lot" in infections or "frequent" in infections):
            is_high_risk = True # Proxy for >= 2
        if "yes" in hospitalized:
            is_high_risk = True

        # 3. Determine Symptom Burden (mMRC >= 2 equivalent)
        # Q: "Do you ever have to stop walking just to catch your breath?" -> mMRC Grade 2
        is_high_symptoms = "yes" in stop_for_breath

        # 4. Classification
        if is_high_risk:
            group = "Group E (High Risk)"
            severity = "HIGH"
            treatment = (
                "**Recommendation for Group E:**\n"
                "- **Primary:** LABA + LAMA combination therapy.\n"
                "- **Consider:** Inhaled Corticosteroids (ICS) if blood eosinophils >= 300.\n"
                "- **Action:** This indicates significant risk. Specialist review recommended."
            )
        elif is_high_symptoms:
            group = "Group B (High Symptoms)"
            severity = "MODERATE"
            treatment = (
                "**Recommendation for Group B:**\n"
                "- **Primary:** LABA + LAMA dual bronchodilation.\n"
                "- **Focus:** Symptom management and pulmonary rehabilitation."
            )
        else:
            group = "Group A (Low Symptoms)"
            severity = "LOW"
            treatment = (
                "**Recommendation for Group A:**\n"
                "- **Primary:** A single Bronchodilator (long or short acting).\n"
                "- **Focus:** Continue if it benefits breathing."
            )

        return {
            "group": group,
            "severity": severity,
            "treatment_guide": treatment
        }

    def generate_recommendations(self, condition: str, qa_data: Dict, severity: str, gold_data: Dict = None) -> str:
        """Generate medical recommendations"""
        
        # specific prompt for COPD with GOLD data
        if condition == "copd" and gold_data:
            return (
                f"{gold_data['treatment_guide']}\n\n"
                "**General Advice:**\n"
                "1. **Smoking Cessation:** If you smoke, this is the single most important step.\n"
                "2. **Vaccinations:** Ensure you have Flu, COVID-19, Pneumococcal, and RSV/Shingles vaccines.\n"
                "3. **Inhaler Technique:** Correct use of your device is crucial. Ask your pharmacist to check.\n"
                "4. **Activity:** Keep active. Walking 20-30 minutes daily is highly beneficial."
            )

        prompt = (
            f"You are a medical AI assistant. Generate recommendations for a patient with {condition}.\n"
            f"Severity: {severity}\n"
            f"Patient Data: {qa_data}\n\n"
            "Provide:\n"
            "1. Immediate actions\n"
            "2. Lifestyle recommendations\n"
            "3. When to seek medical help\n\n"
            "Be concise and clear."
        )
        response = self.llm.invoke(prompt)
        return response.content

    def analyze(self, collected_data: Dict) -> Dict:
        """Analyze collected patient data"""
        condition = collected_data.get("condition_type", "unknown")
        qa_data = collected_data.get("qa_data", {})
        
        gold_result = None
        severity = "MODERATE"

        if condition == "copd":
            gold_result = self.analyze_gold_copd(qa_data)
            severity = gold_result["severity"]
        else:
            severity = self.estimate_severity(qa_data)

        recommendations = self.generate_recommendations(condition, qa_data, severity, gold_result)

        return {
            "condition": condition,
            "severity": severity,
            "gold_group": gold_result.get("group") if gold_result else None,
            "recommendations": recommendations,
            "qa_data": qa_data
        }


# ============================================================
# AGENT 3: PLANNING AGENT
# ============================================================

class PlanningAgent:
    """
    Medical planning agent that creates personalized treatment plans
    based on analysis results.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def create_short_term_plan(self, condition: str, severity: str, qa_data: Dict) -> Dict[str, List[str]]:
        """Create a short-term action plan (1-7 days)"""
        prompt = (
            f"You are a medical AI creating a SHORT-TERM action plan (1-7 days) for a patient with {condition}.\\n"
            f"Severity: {severity}\\n"
            f"Patient Data: {qa_data}\\n\\n"
            "Return ONLY a JSON object with these keys:\\n"
            '{"daily_actions": ["action1", "action2", ...], '
            '"monitoring": ["what to monitor1", "what to monitor2", ...], '
            '"red_flags": ["warning sign1", "warning sign2", ...]}'
        )
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            plan = json.loads(content)
            return {
                "daily_actions": plan.get("daily_actions", []),
                "monitoring": plan.get("monitoring", []),
                "red_flags": plan.get("red_flags", [])
            }
        except Exception:
            return {
                "daily_actions": ["Follow your prescribed medication schedule", "Monitor your symptoms daily"],
                "monitoring": ["Track your vital signs", "Note any changes in symptoms"],
                "red_flags": ["Severe worsening of symptoms", "New concerning symptoms"]
            }
    
    def create_long_term_plan(self, condition: str, severity: str, qa_data: Dict) -> Dict[str, List[str]]:
        """Create a long-term management plan (1-3 months)"""
        prompt = (
            f"You are a medical AI creating a LONG-TERM management plan (1-3 months) for a patient with {condition}.\\n"
            f"Severity: {severity}\\n"
            f"Patient Data: {qa_data}\\n\\n"
            "Return ONLY a JSON object with these keys:\\n"
            '{"lifestyle_changes": ["change1", "change2", ...], '
            '"follow_up_schedule": ["appointment1", "appointment2", ...], '
            '"goals": ["goal1", "goal2", ...]}'
        )
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            plan = json.loads(content)
            return {
                "lifestyle_changes": plan.get("lifestyle_changes", []),
                "follow_up_schedule": plan.get("follow_up_schedule", []),
                "goals": plan.get("goals", [])
            }
        except Exception:
            return {
                "lifestyle_changes": ["Maintain a healthy diet", "Exercise regularly as advised"],
                "follow_up_schedule": ["Schedule regular check-ups with your doctor"],
                "goals": ["Improve overall health", "Manage condition effectively"]
            }
    
    def create_comprehensive_plan(self, analysis_result: Dict) -> Dict[str, Any]:
        """Create a comprehensive treatment plan combining short and long-term strategies"""
        condition = analysis_result.get("condition", "unknown")
        severity = analysis_result.get("severity", "MODERATE")
        qa_data = analysis_result.get("qa_data", {})
        
        short_term = self.create_short_term_plan(condition, severity, qa_data)
        long_term = self.create_long_term_plan(condition, severity, qa_data)
        
        return {
            "condition": condition,
            "severity": severity,
            "short_term_plan": short_term,
            "long_term_plan": long_term,
            "created_at": "now"
        }




# ============================================================
# AGENT 5: NOTIFIER AGENT
# ============================================================

class NotifierAgent:
    """
    Notifier agent that manages medication reminders and notifications
    with Google Calendar integration.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.medications = []
        self.calendar_service = None
    
    def add_medication(self, medication_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a medication to the tracking system
        
        Args:
            medication_data: Dictionary containing:
                - name: Medication name
                - dosage: Dosage amount (e.g., "20mg")
                - frequency: How often (e.g., "twice daily", "every 8 hours")
                - timing: Specific times (e.g., ["08:00", "20:00"])
                - instructions: Special instructions
                - start_date: When to start (optional)
                - duration: How long (optional)
        
        Returns:
            Confirmation with medication ID
        """
        medication_id = len(self.medications) + 1
        
        medication = {
            "id": medication_id,
            "name": medication_data.get("name", ""),
            "dosage": medication_data.get("dosage", ""),
            "frequency": medication_data.get("frequency", ""),
            "timing": medication_data.get("timing", []),
            "instructions": medication_data.get("instructions", ""),
            "start_date": medication_data.get("start_date", "today"),
            "duration": medication_data.get("duration", "ongoing"),
            "active": True
        }
        
        self.medications.append(medication)
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "message": f"Added {medication['name']} to your medication schedule"
        }
    
    def get_medications(self) -> List[Dict[str, Any]]:
        """Get all active medications"""
        return [m for m in self.medications if m.get("active", True)]
    
    def create_medication_schedule(self, medications: List[Dict[str, Any]]) -> str:
        """
        Create a human-readable medication schedule
        
        Args:
            medications: List of medication dictionaries
        
        Returns:
            Formatted schedule text
        """
        if not medications:
            return "No medications scheduled."
        
        prompt = f"""
        You are a medical AI assistant. Create a clear, patient-friendly medication schedule.
        
        Medications: {medications}
        
        Format the schedule as:
        
        MEDICATION SCHEDULE
        ==================
        
        Morning (8:00 AM):
        • [Medication] - [Dosage] - [Instructions]
        
        Afternoon (2:00 PM):
        • [Medication] - [Dosage] - [Instructions]
        
        Evening (8:00 PM):
        • [Medication] - [Dosage] - [Instructions]
        
        IMPORTANT REMINDERS:
        • [Any special instructions]
        
        Make it clear, organized, and easy to follow.
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def generate_reminder_message(self, medication: Dict[str, Any]) -> str:
        """
        Generate a friendly reminder message for a medication
        
        Args:
            medication: Medication dictionary
        
        Returns:
            Reminder message text
        """
        return (
            f"💊 Medication Reminder\n\n"
            f"Time to take: {medication['name']}\n"
            f"Dosage: {medication['dosage']}\n"
            f"Instructions: {medication.get('instructions', 'Take as directed')}\n\n"
            f"✓ Mark as taken when complete"
        )
    
    def setup_google_calendar(self, credentials_path: str = None):
        """
        Set up Google Calendar integration
        
        Args:
            credentials_path: Path to Google Calendar credentials JSON
        
        Note: This is a placeholder. Full implementation requires:
        - Google Calendar API credentials
        - OAuth2 authentication
        - google-api-python-client library
        """
        try:
            # Placeholder for Google Calendar setup
            # In production, you would:
            # 1. Load credentials from credentials_path
            # 2. Authenticate with Google OAuth2
            # 3. Create calendar service
            
            print("⚠️ Google Calendar integration requires setup:")
            print("1. Enable Google Calendar API in Google Cloud Console")
            print("2. Download credentials.json")
            print("3. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            
            return {
                "status": "setup_required",
                "message": "Google Calendar integration not yet configured"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def add_to_google_calendar(self, medication: Dict[str, Any], num_days: int = 30):
        """
        Add medication reminders to Google Calendar
        
        Args:
            medication: Medication dictionary
            num_days: Number of days to create reminders for
        
        Returns:
            Status of calendar event creation
        """
        if not self.calendar_service:
            return {
                "status": "error",
                "message": "Google Calendar not configured. Use setup_google_calendar() first."
            }
        
        # Placeholder for actual Google Calendar API calls
        # In production, you would create recurring events
        
        return {
            "status": "placeholder",
            "message": f"Would create {num_days} days of reminders for {medication['name']}"
        }
    
    def create_notification_plan(self, treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive notification plan based on treatment plan
        
        Args:
            treatment_plan: Treatment plan from PlanningAgent
        
        Returns:
            Notification schedule and reminders
        """
        prompt = f"""
        You are a medical AI creating a notification and reminder plan.
        
        Treatment Plan: {treatment_plan}
        
        Create a notification schedule that includes:
        1. Medication reminders (specific times)
        2. Monitoring reminders (e.g., check blood pressure)
        3. Follow-up appointment reminders
        4. Lifestyle activity reminders
        
        Return JSON ONLY:
        {{
            "medication_reminders": [
                {{"time": "08:00", "action": "Take medication X", "frequency": "daily"}}
            ],
            "monitoring_reminders": [
                {{"time": "09:00", "action": "Check blood pressure", "frequency": "daily"}}
            ],
            "appointment_reminders": [
                {{"date": "2024-12-20", "action": "Cardiology appointment", "time": "14:00"}}
            ],
            "lifestyle_reminders": [
                {{"time": "18:00", "action": "30-minute walk", "frequency": "daily"}}
            ]
        }}
        """
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            plan = json.loads(content)
            return plan
        except Exception:
            return {
                "medication_reminders": [],
                "monitoring_reminders": [],
                "appointment_reminders": [],
                "lifestyle_reminders": []
            }


# ============================================================
# AGENT 5: NOTIFIER AGENT
# ============================================================
# ... (existing NotifierAgent code is above, just ensuring context) ...

# ============================================================
# AGENT 5.5: LAB RESULTS AGENT
# ============================================================

class LabResultsAgent:
    """
    Lab Results Agent that interprets medical lab reports and explains
    findings to the patient in simple terms.
    """
    
    def __init__(self, llm):
        self.llm = llm

    def analyze_lab_report(self, report_text: str, condition: str = "general") -> Dict[str, Any]:
        """
        Analyze the text content of a lab report.
        """
        prompt = (
            f"You are a helpful Medical AI Agent. Analyze this lab report for a patient with: {condition}.\n"
            f"Lab Report Text:\n{report_text}\n\n"
            "Task:\n"
            "1. Identify key biomarkers and their values.\n"
            "2. Flag anything OUTSIDE the normal reference range (High/Low).\n"
            "3. Explain what these mean in simple, patient-friendly language.\n"
            "4. Provide a 'Actionable Advice' summary.\n\n"
            "Return JSON with keys:\n"
            "- 'summary': (String) Brief overview (e.g., 'Your kidney function looks normal, but cholesterol is high').\n"
            "- 'abnormalities': (List of Strings) E.g. ['Glucose: 150 mg/dL (High)', 'Iron: Low'].\n"
            "- 'detailed_analysis': (String) The full explanation.\n"
            "- 'action_items': (List of Strings) What to do next."
        )
        
        response = self.llm.invoke(prompt)
        return parse_llm_output(response.content)

# ============================================================
# AGENT 6: PREDICTION AGENT
# ============================================================

class PredictionAgent:
    """
    Medical prediction agent that forecasts disease progression and
    organ impact based on patient data.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def predict_progression(self, condition: str, qa_data: Dict, current_severity: str) -> Dict[str, Any]:
        """Predict if the case is worsening and how it might progress"""
        prompt = (
            f"You are a medical AI specializing in disease progression. Analyze this case:\\n"
            f"Condition: {condition}\\n"
            f"Current Severity: {current_severity}\\n"
            f"Patient Data: {qa_data}\\n\\n"
            "Predict the likely progression of this condition if untreated or if current trends continue.\\n"
            "Assess if the case is currently worsening based on the symptoms provided.\\n"
            "Return ONLY JSON:\\n"
            '{"worsening": true/false, "progression_forecast": "...", "risk_factors": ["...", "..."]}'
        )
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            return json.loads(content)
        except Exception:
            return {
                "worsening": False,
                "progression_forecast": "Unable to predict progression at this time.",
                "risk_factors": []
            }

    def predict_organ_impact(self, condition: str, qa_data: Dict) -> Dict[str, Any]:
        """Predict which organs are likely to be affected"""
        prompt = (
            f"You are a medical AI. For a patient with {condition} and the following symptoms:\\n"
            f"Patient Data: {qa_data}\\n\\n"
            "Identify which specific organs are at risk or already affected.\\n"
            "Return ONLY JSON:\\n"
            '{"affected_organs": [{"organ": "...", "risk_level": "...", "impact_description": "..."}], '
            '"systemic_risks": "..."}'
        )
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            return json.loads(content)
        except Exception:
            return {
                "affected_organs": [],
                "systemic_risks": "Unable to assess systemic risks."
            }

    def generate_comprehensive_prediction(self, analysis_result: Dict) -> Dict[str, Any]:
        """Generate a complete prediction report"""
        condition = analysis_result.get("condition", "unknown")
        severity = analysis_result.get("severity", "MODERATE")
        qa_data = analysis_result.get("qa_data", {})
        
        progression = self.predict_progression(condition, qa_data, severity)
        organ_impact = self.predict_organ_impact(condition, qa_data)
        
        return {
            "prediction_type": "progression_and_impact",
            "worsening_prediction": progression,
            "organ_impact_prediction": organ_impact
        }


# ============================================================
# AGENT 4: COORDINATOR AGENT
# ============================================================

class CoordinatorAgent:
    """
    Coordinator agent that orchestrates the workflow between all agents
    and manages the overall consultation process.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.qa_agent = SymptomQAAgent(llm)
        self.analysis_agent = AnalysisAgent(llm)
        self.planning_agent = PlanningAgent(llm)
        self.workflow_state = "initialized"
        self.results = {}
    
    def start_consultation(self, initial_message: str) -> Dict[str, Any]:
        """Start a new medical consultation"""
        self.workflow_state = "interviewing"
        
        # Start interview with QA Agent
        response = self.qa_agent.start_interview(initial_message)
        
        return {
            "status": "interview_started",
            "workflow_state": self.workflow_state,
            "response": response,
            "interview_complete": self.qa_agent.interview_complete
        }
    
    def continue_consultation(self, patient_response: str) -> Dict[str, Any]:
        """Continue the consultation with patient's response"""
        if self.workflow_state != "interviewing":
            return {
                "status": "error",
                "message": "Consultation not in interview state"
            }
        
        # Continue interview
        response = self.qa_agent.continue_interview(patient_response)
        
        # Check if interview is complete
        if self.qa_agent.interview_complete:
            self.workflow_state = "analyzing"
            return {
                "status": "interview_complete",
                "workflow_state": self.workflow_state,
                "response": response,
                "interview_complete": True
            }
        
        return {
            "status": "interview_ongoing",
            "workflow_state": self.workflow_state,
            "response": response,
            "interview_complete": False
        }
    
    def perform_analysis(self) -> Dict[str, Any]:
        """Perform medical analysis on collected data"""
        if self.workflow_state != "analyzing":
            return {
                "status": "error",
                "message": "Workflow not ready for analysis"
            }
        
        # Get collected data from QA agent
        collected_data = self.qa_agent.get_collected_data()
        
        # Perform analysis
        analysis = self.analysis_agent.analyze(collected_data)
        self.results["analysis"] = analysis
        
        self.workflow_state = "planning"
        
        return {
            "status": "analysis_complete",
            "workflow_state": self.workflow_state,
            "analysis": analysis
        }
    
    def create_treatment_plan(self) -> Dict[str, Any]:
        """Create a comprehensive treatment plan"""
        if self.workflow_state != "planning":
            return {
                "status": "error",
                "message": "Workflow not ready for planning"
            }
        
        if "analysis" not in self.results:
            return {
                "status": "error",
                "message": "Analysis must be performed before planning"
            }
        
        # Create comprehensive plan
        plan = self.planning_agent.create_comprehensive_plan(self.results["analysis"])
        self.results["plan"] = plan
        
        self.workflow_state = "complete"
        
        return {
            "status": "plan_complete",
            "workflow_state": self.workflow_state,
            "plan": plan
        }
    
    def get_full_consultation_results(self) -> Dict[str, Any]:
        """Get complete consultation results including all agent outputs"""
        return {
            "workflow_state": self.workflow_state,
            "collected_data": self.qa_agent.get_collected_data(),
            "analysis": self.results.get("analysis", {}),
            "treatment_plan": self.results.get("plan", {}),
            "conversation_history": self.qa_agent.full_conversation
        }
    
    def run_full_consultation(self, initial_message: str, patient_responses: List[str]) -> Dict[str, Any]:
        """
        Run a complete consultation workflow (for testing/automation)
        
        Args:
            initial_message: Patient's initial complaint
            patient_responses: List of patient responses to questions
        
        Returns:
            Complete consultation results
        """
        # Start consultation
        result = self.start_consultation(initial_message)
        
        # Continue interview with responses
        for response in patient_responses:
            if not self.qa_agent.interview_complete:
                result = self.continue_consultation(response)
        
        # Perform analysis if interview is complete
        if self.qa_agent.interview_complete:
            analysis_result = self.perform_analysis()
            
            # Create treatment plan
            plan_result = self.create_treatment_plan()
            
            # Return full results
            return self.get_full_consultation_results()
        
        return {
            "status": "interview_incomplete",
            "message": "More responses needed to complete interview"
        }



# ============================================================
# MAIN FUNCTION (for testing)
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MedTwin Agent System - Test with Coordinator")
    print("=" * 60)
    
    # Initialize (replace with your API key)
    api_key = "your-deepseek-api-key-here"
    llm = initialize_deepseek(api_key)
    
    # Test 1: Individual Agents
    print("\n" + "=" * 60)
    print("TEST 1: Individual Agents")
    print("=" * 60)
    
    qa_agent = SymptomQAAgent(llm)
    analysis_agent = AnalysisAgent(llm)
    planning_agent = PlanningAgent(llm)
    
    print("\nPatient: I have chest pain when I walk")
    response = qa_agent.start_interview("I have chest pain when I walk")
    print(f"Agent: {response}")
    
    # Get analysis
    collected_data = qa_agent.get_collected_data()
    analysis = analysis_agent.analyze(collected_data)
    
    print("\n" + "-" * 60)
    print("Analysis Results:")
    print(f"Condition: {analysis['condition']}")
    print(f"Severity: {analysis['severity']}")
    print(f"Recommendations:\n{analysis['recommendations']}")
    
    # Get treatment plan
    plan = planning_agent.create_comprehensive_plan(analysis)
    print("\n" + "-" * 60)
    print("Treatment Plan:")
    print(f"Short-term actions: {plan['short_term_plan']['daily_actions']}")
    print(f"Long-term goals: {plan['long_term_plan']['goals']}")
    
    # Test 2: Coordinator Agent
    print("\n" + "=" * 60)
    print("TEST 2: Coordinator Agent")
    print("=" * 60)
    
    coordinator = CoordinatorAgent(llm)
    
    print("\nStarting coordinated consultation...")
    result = coordinator.start_consultation("I have chest pain when I walk")
    print(f"Status: {result['status']}")
    print(f"Response: {result['response']}")
    
    print("\n" + "=" * 60)
