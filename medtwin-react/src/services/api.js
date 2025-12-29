import axios from 'axios'

// Base API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add auth token to requests if available
api.interceptors.request.use((config) => {
    let token = null;

    if (config.url.startsWith('/doctor')) {
        token = localStorage.getItem('doctorToken');
    } else if (
        config.url.startsWith('/patient') ||
        config.url.startsWith('/consultation') ||
        config.url.startsWith('/medications') ||
        config.url.startsWith('/calendar') ||
        config.url.startsWith('/agent')
    ) {
        token = localStorage.getItem('patientToken');
    }

    // Fallback to generic token for auth routes or legacy code
    if (!token) {
        token = localStorage.getItem('authToken');
    }

    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Handle response errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.warn("Unauthorized access detected")
        }
        return Promise.reject(error)
    }
)

/**
 * AI Agent API Service
 */
export const agentService = {
    startConsultation: async (initialMessage) => {
        const response = await api.post('/consultation/start', { message: initialMessage })
        return response.data
    },

    continueConsultation: async (consultationId, message) => {
        const response = await api.post(`/consultation/${consultationId}/continue`, { message: message })
        return response.data
    },

    performAnalysis: async (consultationId) => {
        const response = await api.post(`/consultation/${consultationId}/analyze`)
        return response.data
    },

    getPredictions: async (patientId) => {
        const response = await api.get(`/agents/prediction/${patientId}`)
        return response.data
    },

    createCarePlan: async (consultationId) => {
        const response = await api.post(`/consultation/${consultationId}/plan`)
        return response.data
    },

    getTriageScore: async (consultationId) => {
        const response = await api.get(`/agents/triage/${consultationId}`)
        return response.data
    },

    getMedications: async (patientId) => {
        const response = await api.get(`/agents/notifier/medications/${patientId}`)
        return response.data
    },

    updateAdherence: async (medicationId, taken) => {
        const response = await api.post('/agents/notifier/adherence', { medication_id: medicationId, taken: taken })
        return response.data
    },

    interpretLabResults: async (labResultsFile) => {
        const formData = new FormData()
        formData.append('file', labResultsFile)
        const response = await api.post('/agents/lab-results/interpret', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return response.data
    },

    getPatientSummary: async (patientId) => {
        const response = await api.get(`/agents/doctor-assistant/summary/${patientId}`)
        return response.data
    },

    getMedicalTicket: async (consultationId) => {
        const response = await api.get(`/agents/coordinator/ticket/${consultationId}`)
        return response.data
    },
}

/**
 * Authentication API Service
 */
export const authService = {
    login: async (email, password) => {
        const response = await api.post('/auth/login', { email, password })
        if (response.data.access_token) {
            const role = response.data.user.role || 'patient';
            if (role === 'doctor') {
                localStorage.setItem('doctorToken', response.data.access_token)
                localStorage.setItem('doctorUser', JSON.stringify(response.data.user))
            } else {
                localStorage.setItem('patientToken', response.data.access_token)
                localStorage.setItem('patientUser', JSON.stringify(response.data.user))
            }
            localStorage.setItem('authToken', response.data.access_token)
        }
        return response.data
    },

    signup: async (userData) => {
        // Determine endpoint based on role
        const endpoint = userData.role === 'doctor' ? '/auth/register/doctor' : '/auth/register/patient'
        const response = await api.post(endpoint, userData)

        if (response.data.access_token) {
            const role = userData.role || 'patient'
            if (role === 'doctor') {
                localStorage.setItem('doctorToken', response.data.access_token)
                localStorage.setItem('doctorUser', JSON.stringify(response.data.user))
            } else {
                localStorage.setItem('patientToken', response.data.access_token)
                localStorage.setItem('patientUser', JSON.stringify(response.data.user))
            }
            localStorage.setItem('authToken', response.data.access_token)
        }
        return response.data
    },

    logout: (role = 'patient') => {
        if (role === 'doctor') {
            localStorage.removeItem('doctorToken')
            localStorage.removeItem('doctorUser')
        } else {
            localStorage.removeItem('patientToken')
            localStorage.removeItem('patientUser')
        }
        localStorage.removeItem('authToken')
        window.location.href = '/login'
    },

    getCurrentUser: (role = 'patient') => {
        const key = role === 'doctor' ? 'doctorUser' : 'patientUser';
        const userStr = localStorage.getItem(key) || localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null
    },

    isAuthenticated: (role = 'patient') => {
        const key = role === 'doctor' ? 'doctorToken' : 'patientToken';
        return !!(localStorage.getItem(key) || localStorage.getItem('authToken'))
    },
}

/**
 * Patient API Service
 */
export const patientService = {
    getDashboard: async () => {
        const response = await api.get('/patient/dashboard')
        return response.data
    },

    getConsultations: async () => {
        const response = await api.get('/patient/consultations')
        return response.data
    },

    getProfile: async () => {
        const response = await api.get('/patient/profile')
        return response.data
    },

    updateProfile: async (profileData) => {
        const response = await api.put('/patient/profile', profileData)
        return response.data
    },
}

/**
 * Doctor API Service
 */
export const doctorService = {
    getDashboard: async () => {
        const response = await api.get('/doctor/dashboard')
        return response.data
    },

    getMyPatients: async () => {
        const response = await api.get('/doctor/patients')
        return response.data
    },

    getPatientQueue: async () => {
        const response = await api.get('/doctor/queue')
        return response.data
    },

    getTicket: async (ticketId) => {
        const response = await api.get(`/doctor/ticket/${ticketId}`)
        return response.data
    },

    approveTicket: async (ticketId, notes, modifications = null) => {
        const response = await api.post(`/doctor/ticket/${ticketId}/approve`, {
            approved: true,
            doctor_notes: notes,
            care_plan_modifications: modifications
        })
        return response.data
    },
}

/**
 * Calendar API Service
 */
export const calendarService = {
    getStatus: async () => {
        const response = await api.get('/calendar/status')
        return response.data
    },

    getConnectUrl: async () => {
        const response = await api.get('/calendar/connect')
        return response.data
    },

    syncCarePlan: async (consultationId) => {
        const response = await api.post(`/calendar/sync-plan/${consultationId}`)
        return response.data
    },
}

/**
 * Medication API Service
 */
export const medicationService = {
    addMedication: async (medData) => {
        const response = await api.post('/medications/', medData)
        return response.data
    },

    getMedications: async () => {
        const response = await api.get('/medications/')
        return response.data
    }
}

export default api
