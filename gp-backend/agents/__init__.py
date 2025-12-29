"""
Agent initialization and configuration
"""

import os
import sys

# Add parent directory to path to import medtwin_agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .medtwin_agents import initialize_deepseek, SymptomQAAgent, AnalysisAgent, NotifierAgent, PlanningAgent, CoordinatorAgent, LabResultsAgent

# Initialize DeepSeek LLM
def get_llm():
    """Get initialized LLM instance"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    return initialize_deepseek(api_key)

# Global agent instances (initialized on first use)
_llm = None
_symptom_agent = None
_analysis_agent = None
_notifier_agent = None
_planning_agent = None
_lab_results_agent = None

def get_symptom_agent():
    """Get SymptomQAAgent instance"""
    global _llm, _symptom_agent
    if _symptom_agent is None:
        if _llm is None:
            _llm = get_llm()
        _symptom_agent = SymptomQAAgent(_llm)
    return _symptom_agent

def get_analysis_agent():
    """Get AnalysisAgent instance"""
    global _llm, _analysis_agent
    if _analysis_agent is None:
        if _llm is None:
            _llm = get_llm()
        _analysis_agent = AnalysisAgent(_llm)
    return _analysis_agent

def get_notifier_agent():
    """Get NotifierAgent instance"""
    global _llm, _notifier_agent
    if _notifier_agent is None:
        if _llm is None:
            _llm = get_llm()
        _notifier_agent = NotifierAgent(_llm)
    return _notifier_agent

def get_planning_agent():
    """Get PlanningAgent instance"""
    global _llm, _planning_agent
    if _planning_agent is None:
        if _llm is None:
            _llm = get_llm()
        _planning_agent = PlanningAgent(_llm)
    return _planning_agent

def get_coordinator_agent():
    """Get CoordinatorAgent instance"""
    global _llm
    if _llm is None:
        _llm = get_llm()
    return CoordinatorAgent(_llm)

def get_lab_results_agent():
    """Get LabResultsAgent instance"""
    global _llm, _lab_results_agent
    if _lab_results_agent is None:
        if _llm is None:
            _llm = get_llm()
        _lab_results_agent = LabResultsAgent(_llm)
    return _lab_results_agent


