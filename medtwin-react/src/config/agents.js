/**
 * MedTwin AI Agents Configuration
 * 
 * This file defines the 9 specialized AI agents that power the MedTwin platform.
 * Each agent has specific responsibilities in the patient care workflow.
 */

export const AGENTS = {
    // 1. Diagnostic Agent (Symptom Q&A)
    DIAGNOSTIC: {
        id: 'diagnostic',
        name: 'Diagnostic Agent',
        description: 'Conducts intelligent symptom interviews and identifies conditions',
        icon: '🔍',
        color: '#A8B5A0', // Sage green
        endpoint: '/api/agents/diagnostic',
        capabilities: [
            'Natural language symptom analysis',
            'Medical condition identification',
            'Structured data extraction',
            'COPD, Diabetes, Heart Disease detection'
        ]
    },

    // 2. Analysis & Simulation Agent
    ANALYSIS: {
        id: 'analysis',
        name: 'Analysis & Simulation Agent',
        description: 'Evaluates patient data against clinical standards',
        icon: '📊',
        color: '#6B46C1', // Royal purple
        endpoint: '/api/agents/analysis',
        capabilities: [
            'Severity assessment (Low to Critical)',
            'Clinical standards evaluation',
            'Outcome simulation',
            'Risk stratification'
        ]
    },

    // 3. Planner Agent
    PLANNER: {
        id: 'planner',
        name: 'Planner Agent',
        description: 'Creates personalized care plans',
        icon: '📋',
        color: '#D4AF37', // Champagne gold
        endpoint: '/api/agents/planner',
        capabilities: [
            'Short-term action plans (1-7 days)',
            'Long-term management (1-3 months)',
            'Personalized care strategies',
            'Goal setting and tracking'
        ]
    },

    // 4. Prediction & Cognitive Agent
    PREDICTION: {
        id: 'prediction',
        name: 'Prediction & Cognitive Agent',
        description: 'Forecasts long-term health risks',
        icon: '🔮',
        color: '#E8B4B8', // Rose gold
        endpoint: '/api/agents/prediction',
        capabilities: [
            'Long-term risk prediction',
            'Disease progression forecasting',
            'Organ-specific impact analysis',
            '5-year outcome modeling'
        ]
    },

    // 5. Triage & Safety Agent
    TRIAGE: {
        id: 'triage',
        name: 'Triage & Safety Agent',
        description: 'Analyzes urgency and prioritizes cases',
        icon: '🚨',
        color: '#F4A89F', // Coral
        endpoint: '/api/agents/triage',
        capabilities: [
            'Urgency score calculation',
            'Red flag detection',
            'Priority queue management',
            'Emergency escalation'
        ]
    },

    // 6. Treatment & Notifier Agent
    NOTIFIER: {
        id: 'notifier',
        name: 'Treatment & Notifier Agent',
        description: 'Manages medication tracking and reminders',
        icon: '💊',
        color: '#10B981', // Emerald
        endpoint: '/api/agents/notifier',
        capabilities: [
            'Medication adherence tracking',
            'Google Calendar integration',
            'Smart reminders',
            'Compliance monitoring'
        ]
    },

    // 7. Doctor Assistant Agent
    DOCTOR_ASSISTANT: {
        id: 'doctor_assistant',
        name: 'Doctor Assistant Agent',
        description: 'Provides clinical decision support',
        icon: '👨‍⚕️',
        color: '#3B82F6', // Blue
        endpoint: '/api/agents/doctor-assistant',
        capabilities: [
            'Executive summaries',
            'Differential diagnosis',
            'Diagnostic test suggestions',
            'Clinical workflow optimization'
        ]
    },

    // 8. Lab Results Agent
    LAB_RESULTS: {
        id: 'lab_results',
        name: 'Lab Results Agent',
        description: 'Interprets complex lab reports',
        icon: '🧪',
        color: '#8B5CF6', // Purple
        endpoint: '/api/agents/lab-results',
        capabilities: [
            'Biomarker interpretation',
            'Simple language explanations',
            'Critical value highlighting',
            'Trend analysis'
        ]
    },

    // 9. Coordinator Agent (The Boss)
    COORDINATOR: {
        id: 'coordinator',
        name: 'Coordinator Agent',
        description: 'Orchestrates all agents and manages the complete health journey',
        icon: '🎯',
        color: '#D4AF37', // Champagne gold (premium)
        endpoint: '/api/agents/coordinator',
        capabilities: [
            'Multi-agent orchestration',
            'Workflow management',
            'Medical ticket creation',
            'Doctor-patient synchronization',
            'Complete story consolidation'
        ]
    }
}

/**
 * Agent Workflow Stages
 * Defines the patient journey through the agent system
 */
export const WORKFLOW_STAGES = {
    CONSULTATION: {
        name: 'Consultation',
        agents: [AGENTS.DIAGNOSTIC, AGENTS.COORDINATOR],
        description: 'Initial symptom interview and data collection'
    },
    ANALYSIS: {
        name: 'Analysis',
        agents: [AGENTS.ANALYSIS, AGENTS.PREDICTION, AGENTS.TRIAGE],
        description: 'Medical analysis, risk assessment, and prioritization'
    },
    PLANNING: {
        name: 'Planning',
        agents: [AGENTS.PLANNER, AGENTS.NOTIFIER],
        description: 'Care plan creation and medication management'
    },
    DOCTOR_REVIEW: {
        name: 'Doctor Review',
        agents: [AGENTS.DOCTOR_ASSISTANT, AGENTS.COORDINATOR],
        description: 'Clinical review and approval'
    },
    ONGOING_CARE: {
        name: 'Ongoing Care',
        agents: [AGENTS.NOTIFIER, AGENTS.LAB_RESULTS, AGENTS.PREDICTION],
        description: 'Continuous monitoring and optimization'
    }
}

/**
 * Get agent by ID
 */
export const getAgent = (agentId) => {
    return Object.values(AGENTS).find(agent => agent.id === agentId)
}

/**
 * Get all agents as array
 */
export const getAllAgents = () => {
    return Object.values(AGENTS)
}

/**
 * Get agents for specific workflow stage
 */
export const getAgentsForStage = (stageName) => {
    return WORKFLOW_STAGES[stageName]?.agents || []
}

export default AGENTS
