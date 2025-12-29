"""
MedTwin - Medical Assistant Agent System
Powered by DeepSeek AI
"""

import os
import json
import re
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI

# ============================================================
# CONFIGURATION & FALLBACK
# ============================================================

class MockLLM:
    """Fallback Mock for system stability"""
    def invoke(self, prompt):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse("Simulated Response: DeepSeek connection not established.")

def initialize_deepseek(api_key: str = None):
    if api_key: os.environ["DEEPSEEK_API_KEY"] = api_key
    key = os.environ.get("DEEPSEEK_API_KEY")
    
    if not key or "sk-" not in key:
        print("[LLM] No valid API key found. Using MockLLM.")
        return MockLLM()
    
    print(f"[LLM] Initializing DeepSeek with key: {key[:8]}...")
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=key,
        base_url="https://api.deepseek.com",
        temperature=0.3,
        max_tokens=2000,
        timeout=20
    )

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
# AGENT 1: SYMPTOM Q&A AGENT (The Heart of your system)
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
        self.awaiting_disambiguation = False
        self.possible_conditions = []

    def rule_based_extract(self, text: str):
        text_lower = text.lower()
        if re.search(r"\b(smoke|smoking|smoker|cigarette)\b", text_lower): self.extracted_info["smoking"] = "yes"
        if re.search(r"\b(non-smoker|never smoke|quit smoking)\b", text_lower): self.extracted_info["smoking"] = "no"
        if re.search(r"\b(cough|phlegm|mucus)\b", text_lower): self.extracted_info["cough"] = text
        if re.search(r"\b(breath|breathe|shortness of breath)\b", text_lower): self.extracted_info["breathing"] = text

    def llm_synonym_extract(self, text: str):
        prompt = (
            "Extract medical symptoms and facts. Return JSON ONLY: "
            '{"extracted_facts": {"smoking": "yes/no/unknown", "symptoms": ["..."]}} '
            f'Message: "{text}"'
        )
        try:
            raw = self.llm.invoke(prompt).content.strip()
            data = json.loads(raw)
            if "extracted_facts" in data: self.extracted_info.update(data["extracted_facts"])
        except: pass

    def should_skip_question(self, question: str) -> bool:
        q = question.lower()
        if ("smoke" in q or "smoking" in q) and "smoking" in self.extracted_info: return True
        if "cough" in q and "cough" in self.extracted_info: return True
        return False

    def identify_condition(self, text: str) -> str | None:
        t = text.lower()
        if any(w in t for w in ["diabet", "sugar", "glucose"]): self.condition_type = "diabetes"
        elif any(w in t for w in ["hypertens", "blood pressure", "bp"]): self.condition_type = "hypertension"
        elif any(w in t for w in ["heart", "chest pain", "cardiac"]): self.condition_type = "heart_disease"
        elif any(w in t for w in ["copd", "breath", "smoke", "lung"]): self.condition_type = "copd"
        return self.condition_type

    def get_next_question(self) -> str | None:
        if not self.condition_type: return None
        qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
        while self.current_question_index < len(qs):
            q = qs[self.current_question_index]
            if self.should_skip_question(q):
                self.current_question_index += 1
                continue
            return q
        self.interview_complete = True
        return None

    def start_interview(self, initial_message: str) -> str:
        self.rule_based_extract(initial_message)
        self.llm_synonym_extract(initial_message)
        self.identify_condition(initial_message)
        if not self.condition_type:
            self.interview_complete = True
            return "I can assist with diabetes, hypertension, heart disease, or COPD. Which concern should we discuss?"
        q = self.get_next_question()
        return q if q else "Thank you. Analysis starting..."

    def continue_interview(self, patient_response: str) -> str:
        qs = MEDICAL_QUESTIONS.get(self.condition_type, [])
        if self.current_question_index < len(qs):
            self.answers[qs[self.current_question_index]] = patient_response
        self.current_question_index += 1
        q = self.get_next_question()
        return q if q else "Interview complete. Analysis starting..."

    def get_collected_data(self) -> Dict:
        return {"condition_type": self.condition_type, "qa_data": {**self.answers, **self.extracted_info}}

# ============================================================
# AGENT 2: ANALYSIS AGENT
# ============================================================

class AnalysisAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, collected_data: Dict) -> Dict:
        """Analyze collected patient data using DeepSeek AI"""
        condition = collected_data.get("condition_type", "unknown")
        qa_data = collected_data.get("qa_data", {})
        
        prompt = (
            f"You are a specialized Medical Analysis AI. Carefully review this patient data for {condition}:\n"
            f"Data: {json.dumps(qa_data)}\n\n"
            "Task:\n"
            "1. Assess the severity level (LOW, MODERATE, HIGH, CRITICAL).\n"
            "2. Provide a detailed medical reasoning for the severity.\n"
            "3. Generate specific, actionable medical recommendations based on guidelines.\n\n"
            "Return JSON ONLY with this structure:\n"
            "{\n"
            '  "condition": "...",\n'
            '  "severity": "LOW/MODERATE/HIGH/CRITICAL",\n'
            '  "recommendations": "Detailed multi-line string here",\n'
            '  "reasoning": "...",\n'
            '  "qa_data": { ... }\n'
            "}"
        )
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            # Clean possible markdown blocks
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
                
            analysis = json.loads(content)
            # Ensure it has the original qa_data
            analysis["qa_data"] = qa_data
            return analysis
        except Exception as e:
            print(f"[ERROR] AnalysisAgent failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "condition": condition,
                "severity": "MODERATE",
                "recommendations": "Based on our preliminary screening, please focus on managing your symptoms and maintain a daily health log. We recommend scheduling a formal consultation with your healthcare provider for a comprehensive diagnostic review.",
                "reasoning": "System fallback due to processing error.",
                "qa_data": qa_data
            }

# ============================================================
# AGENT 3: PLANNING AGENT
# ============================================================

class PlanningAgent:
    def __init__(self, llm):
        self.llm = llm

    def create_comprehensive_plan(self, analysis_result: Dict) -> Dict:
        """Create a personalized care plan using DeepSeek AI"""
        condition = analysis_result.get("condition", "unknown")
        severity = analysis_result.get("severity", "MODERATE")
        qa_data = analysis_result.get("qa_data", {})

        prompt = (
            f"You are a Medical Care Planner AI. create a PERSONALIZED care plan for a patient with {condition}.\n"
            f"Current Severity: {severity}\n"
            f"Patient Context: {json.dumps(qa_data)}\n\n"
            "Generate a structured plan including:\n"
            "- Short-term immediate actions (1-7 days)\n"
            "- Monitoring requirements\n"
            "- Red flags to watch for\n"
            "- Goals for the patient\n"
            "- Long-term management strategies\n\n"
            "Return JSON ONLY with this structure:\n"
            "{\n"
            '  "short_term_plan": {\n'
            '    "daily_actions": ["..."],\n'
            '    "monitoring": ["..."],\n'
            '    "red_flags": ["..."],\n'
            '    "goals": ["..."]\n'
            '  },\n'
            '  "long_term_plan": {\n'
            '    "goals": ["..."],\n'
            '    "lifestyle_changes": ["..."]\n'
            '  }\n'
            "}"
        )

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
                
            return json.loads(content)
        except Exception as e:
            print(f"[ERROR] PlanningAgent failed: {e}")
            return {
                "short_term_plan": {
                    "daily_actions": ["Monitor symptoms daily", "Stay hydrated", "Follow existing medications"],
                    "goals": ["Stabilize current symptoms", "Prepare for doctor visit"]
                },
                "long_term_plan": {
                    "goals": ["Improve overall wellness", "Better condition control"],
                    "lifestyle_changes": ["Consistent physical activity", "Balanced nutritional intake"]
                }
            }

# ============================================================
# REMAINING AGENTS (Stubs for system completeness)
# ============================================================

class NotifierAgent:
    def __init__(self, llm):
        self.llm = llm

    def schedule_care_plan(self, user_email: str, plan: Dict) -> Dict:
        """Schedule daily actions from care plan into Google Calendar"""
        try:
            from utils.google_calendar import calendar_service
            
            # Check if calendar is connected
            status = calendar_service.check_calendar_connection(user_email)
            if not status.get('connected'):
                return {
                    "success": False, 
                    "error": "Calendar not connected", 
                    "auth_url": calendar_service.get_authorization_url(user_email).get('authorization_url')
                }

            short_term = plan.get("short_term_plan", {})
            actions = short_term.get("daily_actions", [])
            monitoring = short_term.get("monitoring", [])
            
            all_reminders = []
            
            # 1. Schedule Actions
            for action in actions:
                med_data = {
                    "name": action,
                    "dosage": "Action Required",
                    "instructions": "MedTwin Daily Care Task",
                    "timing": ["09:00"] # Default morning time
                }
                res = calendar_service.create_medication_reminders(user_email, med_data, num_days=7)
                all_reminders.append(res)
                
            # 2. Schedule Monitoring
            for task in monitoring:
                med_data = {
                    "name": f"Monitor: {task}",
                    "dosage": "Check and Record",
                    "instructions": "MedTwin Monitoring Task",
                    "timing": ["10:00"]
                }
                res = calendar_service.create_medication_reminders(user_email, med_data, num_days=7)
                all_reminders.append(res)
                
            return {"success": True, "reminders_created": len(all_reminders), "details": all_reminders}
            
        except Exception as e:
            print(f"[ERROR] NotifierAgent failed: {e}")
            return {"success": False, "error": str(e)}

    def get_medications(self): return []

class LabResultsAgent:
    """
    Lab Results Interpretation Agent
    Analyzes lab test results and provides medical interpretation with OCR support
    """
    def __init__(self, llm):
        self.llm = llm
        
    def analyze_document(self, file_content, filename, content_type):
        """
        Analyze lab results document with OCR support
        
        Args:
            file_content: Binary file content
            filename: Name of the file
            content_type: MIME type of the file
            
        Returns:
            dict with interpretation, extracted_text, abnormal_values, etc.
        """
        import io
        
        try:
            # Extract text based on file type
            extracted_text = None
            
            if 'text/plain' in content_type or filename.endswith('.txt'):
                # Text file - direct decode
                extracted_text = file_content.decode('utf-8', errors='ignore')
                
            elif 'image' in content_type or filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Image file - use OCR
                try:
                    import pytesseract
                    from PIL import Image
                    
                    # Try to find Tesseract executable
                    import os
                    tesseract_paths = [
                        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                        r'C:\Tesseract-OCR\tesseract.exe'
                    ]
                    
                    for path in tesseract_paths:
                        if os.path.exists(path):
                            pytesseract.pytesseract.tesseract_cmd = path
                            break
                    
                    # Open image from bytes
                    image = Image.open(io.BytesIO(file_content))
                    extracted_text = pytesseract.image_to_string(image)
                    
                except ImportError:
                    return {
                        "status": "error",
                        "message": "OCR libraries not installed. Please upload a text file instead."
                    }
                except Exception as ocr_error:
                    return {
                        "status": "error",
                        "message": f"OCR failed: {str(ocr_error)}. Tesseract may not be installed.",
                        "tip": "Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
                    }
                    
            elif 'pdf' in content_type or filename.lower().endswith('.pdf'):
                # PDF file - use OCR
                try:
                    import pytesseract
                    from PIL import Image
                    from pdf2image import convert_from_bytes
                    import os
                    
                    # Find Tesseract
                    tesseract_paths = [
                        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                        r'C:\Tesseract-OCR\tesseract.exe'
                    ]
                    
                    for path in tesseract_paths:
                        if os.path.exists(path):
                            pytesseract.pytesseract.tesseract_cmd = path
                            break
                    
                    # Convert PDF to images
                    images = convert_from_bytes(file_content, dpi=300)
                    
                    # Extract text from each page
                    text_parts = []
                    for i, image in enumerate(images):
                        page_text = pytesseract.image_to_string(image)
                        text_parts.append(f"--- Page {i+1} ---\n{page_text}")
                    
                    extracted_text = "\n\n".join(text_parts)
                    
                except ImportError:
                    return {
                        "status": "error",
                        "message": "PDF/OCR libraries not installed. Please upload a text file instead."
                    }
                except Exception as pdf_error:
                    return {
                        "status": "error",
                        "message": f"PDF processing failed: {str(pdf_error)}",
                        "tip": "Ensure Tesseract OCR and Poppler are installed"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported file type: {content_type}"
                }
            
            # Validate extracted text
            if not extracted_text or len(extracted_text.strip()) < 10:
                return {
                    "status": "error",
                    "message": "No readable text found in the document"
                }
            
            # Interpret the results
            interpretation = self.interpret_results(extracted_text)
            
            return {
                "status": "success",
                "extracted_text": extracted_text,
                "interpretation": interpretation.get("interpretation", ""),
                "abnormal_values": interpretation.get("abnormal_values", []),
                "recommendations": interpretation.get("recommendations", ""),
                "follow_up_required": interpretation.get("follow_up_required", False),
                "follow_up_message": interpretation.get("follow_up_message", "")
            }
            
        except Exception as e:
            print(f"[ERROR] Document analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }
        
    def interpret_results(self, lab_text, condition="general"):
        """
        Interpret lab results from text with patient-friendly explanations
        
        Args:
            lab_text: String containing lab test results
            condition: Patient's condition category (e.g., "diabetic", "heart", "general")
            
        Returns:
            dict with interpretation, abnormal_values, recommendations, etc.
        """
        prompt = f"""You are a helpful Medical AI Agent. Analyze this lab report for a patient with: {condition}.

Lab Report Text:
{lab_text}

Task:
1. Identify key biomarkers and their values.
2. Flag anything OUTSIDE the normal reference range (High/Low).
3. Explain what these mean in simple, patient-friendly language.
4. Provide actionable advice.

Return JSON with these exact keys:
{{
    "summary": "Brief overview in simple terms (e.g., 'Your kidney function looks normal, but cholesterol is high')",
    "abnormalities": [
        {{"test": "Test Name", "value": "Value", "unit": "Unit", "reference": "Normal Range", "significance": "What this means in simple terms"}}
    ],
    "detailed_analysis": "Full explanation of all test results in patient-friendly language",
    "action_items": [
        "Specific actionable recommendations (e.g., 'Schedule follow-up with cardiologist')"
    ],
    "follow_up_required": true,
    "follow_up_message": "Reason if follow-up needed"
}}

Be professional, clear, compassionate, and prioritize patient safety."""

        try:
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to find JSON in the response
            import json
            import re
            
            # Look for JSON block
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                
                # Map to expected format for frontend compatibility
                return {
                    "interpretation": result.get("detailed_analysis", result.get("summary", "")),
                    "abnormal_values": result.get("abnormalities", []),
                    "recommendations": "\n".join(result.get("action_items", [])),
                    "follow_up_required": result.get("follow_up_required", len(result.get("abnormalities", [])) > 0),
                    "follow_up_message": result.get("follow_up_message", ""),
                    "summary": result.get("summary", "")
                }
            else:
                # Fallback if no proper JSON
                return {
                    "interpretation": content,
                    "abnormal_values": [],
                    "recommendations": "Please consult with your healthcare provider for detailed interpretation.",
                    "follow_up_required": True,
                    "follow_up_message": "Professional review recommended",
                    "summary": "Analysis completed - please review with your doctor"
                }
            
        except Exception as e:
            print(f"[ERROR] Lab results interpretation failed: {e}")
            return {
                "interpretation": f"Error interpreting results: {str(e)}",
                "abnormal_values": [],
                "recommendations": "Please consult with your healthcare provider.",
                "follow_up_required": True,
                "follow_up_message": "Unable to automatically interpret results",
                "summary": "Error during analysis"
            }



class PredictionAgent:
    def __init__(self, llm): pass

class CoordinatorAgent:
    """
    Coordinator Agent - Creates comprehensive medical tickets
    Combines all agent outputs into a structured medical report
    """
    def __init__(self, llm):
        self.llm = llm
    
    def create_medical_ticket(self, consultation_data: Dict) -> Dict:
        """
        Create a comprehensive medical ticket from all agent outputs
        Input: consultation_data with analysis_result and care_plan
        Output: Complete medical ticket for doctor review
        """
        try:
            analysis = consultation_data.get('analysis_result', {})
            care_plan = consultation_data.get('care_plan', {})
            collected_data = consultation_data.get('collected_data', {})
            conversation_history = consultation_data.get('conversation_history', [])
            
            # Generate doctor-facing summary using LLM
            prompt = (
                "You are a Medical Coordinator AI. Create a comprehensive medical ticket summary for doctor review.\n\n"
                f"Patient Interview Data: {json.dumps(collected_data)}\n"
                f"AI Analysis: {json.dumps(analysis)}\n"
                f"Proposed Care Plan: {json.dumps(care_plan)}\n\n"
                "Generate a concise doctor-facing summary including:\n"
                "1. Chief Complaint\n"
                "2. Key Symptoms\n"
                "3. AI Assessment\n"
                "4. Recommended Actions\n"
                "5. Urgency Level\n\n"
                "Return JSON ONLY with this structure:\n"
                "{\n"
                '  "chief_complaint": "...",\n'
                '  "key_symptoms": ["...", "..."],\n'
                '  "ai_assessment": "...",\n'
                '  "urgency": "LOW/MODERATE/HIGH/CRITICAL",\n'
                '  "doctor_notes": "..."\n'
                "}"
            )
            
            try:
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                elif content.startswith("```"):
                    content = content.replace("```", "").strip()
                
                ticket_summary = json.loads(content)
            except Exception as e:
                print(f"[WARN] LLM summary generation failed, using fallback: {e}")
                ticket_summary = {
                    "chief_complaint": collected_data.get('condition_type', 'General consultation'),
                    "key_symptoms": list(collected_data.get('qa_data', {}).values())[:5],
                    "ai_assessment": analysis.get('recommendations', 'Pending analysis'),
                    "urgency": analysis.get('severity', 'MODERATE'),
                    "doctor_notes": "AI-generated ticket from patient consultation"
                }
            
            # Build complete ticket
            medical_ticket = {
                "ticket_id": consultation_data.get('id'),
                "patient_id": consultation_data.get('patient_id'),
                "created_at": consultation_data.get('created_at'),
                "status": "pending_review",
                
                # Summary for quick review
                "summary": ticket_summary,
                
                # Complete diagnostic data
                "diagnostic_data": {
                    "condition_type": collected_data.get('condition_type'),
                    "interview_data": collected_data.get('qa_data', {}),
                    "conversation_transcript": conversation_history
                },
                
                # AI Analysis
                "ai_analysis": {
                    "severity": analysis.get('severity'),
                    "condition": analysis.get('condition'),
                    "recommendations": analysis.get('recommendations'),
                    "reasoning": analysis.get('reasoning')
                },
                
                # Care Plan
                "proposed_care_plan": {
                    "short_term": care_plan.get('short_term_plan', {}),
                    "long_term": care_plan.get('long_term_plan', {})
                },
                
                # Metadata
                "requires_doctor_approval": True,
                "priority_score": self._calculate_priority(analysis.get('severity', 'MODERATE'))
            }
            
            return medical_ticket
            
        except Exception as e:
            print(f"[ERROR] CoordinatorAgent ticket creation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "ticket_id": consultation_data.get('id'),
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_priority(self, severity: str) -> int:
        """Calculate priority score based on severity"""
        priority_map = {
            "CRITICAL": 1,
            "HIGH": 2,
            "MODERATE": 3,
            "LOW": 4
        }
        return priority_map.get(severity, 3)


