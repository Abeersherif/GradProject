import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../services/api'
import Navbar from '../components/Navbar'
import './SignUpPage.css'

const SignUpPage = () => {
    const navigate = useNavigate()
    const [currentStep, setCurrentStep] = useState(1)
    const [selectedRole, setSelectedRole] = useState('')
    const [selectedDiseases, setSelectedDiseases] = useState([])

    const [formData, setFormData] = useState({
        // Common fields
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',

        // Personal Information
        age: '',
        sex: '',
        occupation: '',
        maritalStatus: '',
        specialHabits: '',

        // Medical Information
        bloodType: '',

        // Diabetes - Comprehensive Fields
        diabetesType: '',
        diabetesDiagnosisYear: '',
        diabetesLastHbA1c: '',
        diabetesLastFBS: '',
        diabetesCurrentMedications: '',
        diabetesInsulinUsage: '',
        diabetesInsulinDose: '',
        diabetesComplications: '',
        diabetesDietPlan: '',
        diabetesExerciseRoutine: '',
        diabetesBloodSugarMonitoring: '',
        diabetesHypoglycemiaFrequency: '',

        // COPD - Comprehensive Fields
        copdSeverity: '',
        copdDiagnosisYear: '',
        copdLastFEV1: '',
        copdCurrentMedications: '',
        copdInhalerTypes: '',
        copdOxygenTherapy: '',
        copdOxygenFlowRate: '',
        copdSmokingStatus: '',
        copdPackYears: '',
        copdExacerbationFrequency: '',
        copdActivityLimitation: '',
        copdBreathlessnessScore: '',

        // Heart Disease - Comprehensive Fields
        heartDiseaseType: '',
        heartDiseaseDiagnosisYear: '',
        heartDiseaseLastEjectionFraction: '',
        heartDiseaseCurrentMedications: '',
        heartDiseaseStentPlacement: '',
        heartDiseaseSurgeryHistory: '',
        heartDiseaseLastECGDate: '',
        heartDiseaseLastStressTestDate: '',
        heartDiseaseChestPainFrequency: '',
        heartDiseaseActivityTolerance: '',
        heartDiseaseRiskFactors: '',

        // Doctor fields
        licenseNumber: '',
        specialty: '',
        hospital: '',
        yearsExperience: '',
        bio: '',
        clinicAddress: ''
    })

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const steps = [
        { number: 1, label: 'Role', icon: '🔐' },
        { number: 2, label: 'Personal', icon: '👤' },
        { number: 3, label: 'Medical', icon: '🏥' },
        { number: 4, label: 'Done', icon: '✓' }
    ]

    const diseases = [
        {
            id: 'diabetes',
            name: 'Diabetes Type 2',
            icon: '🩸',
            description: 'A chronic condition affecting how your body processes blood sugar (glucose). Type 2 diabetes occurs when your body becomes resistant to insulin or doesn\'t produce enough insulin.'
        },
        {
            id: 'copd',
            name: 'COPD',
            icon: '🫁',
            description: 'Chronic Obstructive Pulmonary Disease - a group of lung diseases that block airflow and make breathing difficult. Includes chronic bronchitis and emphysema.'
        },
        {
            id: 'heartDisease',
            name: 'Coronary Artery Disease',
            icon: '❤️',
            description: 'The most common type of heart disease, occurs when the arteries that supply blood to your heart become narrowed or blocked due to plaque buildup.'
        }
    ]

    const doctorSpecialties = [
        { id: 'endocrinology', name: 'Diabetic Specialist', icon: '🩸', description: 'Specialized in managing diabetes and metabolic disorders.' },
        { id: 'cardiology', name: 'Cardiologist', icon: '❤️', description: 'Expert in heart health, arrhythmias, and cardiovascular care.' },
        { id: 'pulmonology', name: 'COPD / Lung Specialist', icon: '🫁', description: 'Focused on respiratory health, COPD, and lung conditions.' }
    ]

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
    }

    const toggleDisease = (diseaseId) => {
        setSelectedDiseases(prev =>
            prev.includes(diseaseId)
                ? prev.filter(id => id !== diseaseId)
                : [...prev, diseaseId]
        )
    }

    const validateStep = () => {
        if (currentStep === 1 && !selectedRole) {
            setError('Please select a role to continue')
            return false
        }

        if (currentStep === 2) {
            if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
                setError('Please fill in all required fields')
                return false
            }

            if (formData.password !== formData.confirmPassword) {
                setError('Passwords do not match')
                return false
            }

            if (formData.password.length < 8) {
                setError('Password must be at least 8 characters')
                return false
            }
        }

        setError('')
        return true
    }

    const nextStep = () => {
        if (validateStep()) {
            setCurrentStep(prev => Math.min(prev + 1, 4))
        }
    }

    const prevStep = () => {
        setCurrentStep(prev => Math.max(prev - 1, 1))
        setError('')
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!validateStep()) return

        setLoading(true)
        try {
            const userData = {
                ...formData,
                role: selectedRole,
                diseases: selectedDiseases
            }

            // Call backend signup API
            const response = await authService.signup(userData)

            // Save tokens and user data with role-specific keys
            if (selectedRole === 'patient') {
                localStorage.setItem('patientToken', response.access_token)
                localStorage.setItem('patientUser', JSON.stringify(response.user || {
                    id: response.userId,
                    fullName: `${formData.firstName} ${formData.lastName}`,
                    email: formData.email,
                    role: 'patient'
                }))
            } else {
                localStorage.setItem('doctorToken', response.access_token)
                localStorage.setItem('doctorUser', JSON.stringify(response.user || {
                    id: response.userId,
                    fullName: `${formData.firstName} ${formData.lastName}`,
                    email: formData.email,
                    role: 'doctor'
                }))
            }

            // Also store in legacy keys for compatibility
            localStorage.setItem('authToken', response.access_token)
            localStorage.setItem('user', JSON.stringify(response.user || {
                id: response.userId,
                fullName: `${formData.firstName} ${formData.lastName}`,
                email: formData.email,
                role: selectedRole
            }))

            // Show success
            setCurrentStep(4)
            setTimeout(() => {
                if (selectedRole === 'patient') {
                    navigate('/patient/dashboard')
                } else {
                    navigate('/doctor/dashboard')
                }
            }, 2000)
        } catch (err) {
            console.error('Signup error:', err)
            setError(err.response?.data?.error || err.message || 'Sign up failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page signup-page">
            <Navbar />

            <div className="auth-container">
                <div className="signup-wrapper">
                    {/* Stepper */}
                    <div className="stepper">
                        {steps.map((step, index) => (
                            <div key={step.number}>
                                <div className={`stepper-item ${currentStep >= step.number ? 'active' : ''} ${currentStep > step.number ? 'completed' : ''}`}>
                                    <div className="stepper-circle">
                                        {currentStep > step.number ? '✓' : step.icon}
                                    </div>
                                    <span className="stepper-label">{step.label}</span>
                                </div>
                                {index < steps.length - 1 && (
                                    <div className={`stepper-line ${currentStep > step.number ? 'completed' : ''}`}></div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Form Container */}
                    <div className="auth-box signup-box">
                        {error && (
                            <div className="error-message">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
                                    <path d="M10 6V10M10 14H10.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            {/* Step 1: Role Selection */}
                            {currentStep === 1 && (
                                <div className="step-content fade-in">
                                    <div className="auth-header">
                                        <h1 className="auth-title">Choose Your Role</h1>
                                        <p className="auth-subtitle">Select how you'll be using MedTwin</p>
                                    </div>

                                    <div className="role-cards">
                                        <div
                                            className={`role-card ${selectedRole === 'patient' ? 'selected' : ''}`}
                                            onClick={() => setSelectedRole('patient')}
                                        >
                                            <div className="role-icon patient-icon">
                                                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                                                    <circle cx="24" cy="14" r="8" stroke="currentColor" strokeWidth="2.5" />
                                                    <path d="M10 38C10 30 15 26 24 26C33 26 38 30 38 38" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                                                </svg>
                                            </div>
                                            <h3 className="role-title">Patient</h3>
                                            <p className="role-description">
                                                Monitor your health, get AI-powered insights, and manage your care plan.
                                            </p>
                                            {selectedRole === 'patient' && (
                                                <div className="role-check">
                                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                                        <path d="M5 13L9 17L19 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                                                    </svg>
                                                </div>
                                            )}
                                        </div>

                                        <div
                                            className={`role-card ${selectedRole === 'doctor' ? 'selected' : ''}`}
                                            onClick={() => setSelectedRole('doctor')}
                                        >
                                            <div className="role-icon doctor-icon">
                                                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                                                    <path d="M24 8L24 40M8 24L40 24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                                                    <circle cx="24" cy="24" r="10" stroke="currentColor" strokeWidth="2.5" />
                                                </svg>
                                            </div>
                                            <h3 className="role-title">Doctor</h3>
                                            <p className="role-description">
                                                Access AI-assisted diagnostics, manage patients, and streamline your workflow.
                                            </p>
                                            {selectedRole === 'doctor' && (
                                                <div className="role-check">
                                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                                        <path d="M5 13L9 17L19 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <button type="button" onClick={nextStep} className="btn btn-primary btn-large btn-full">
                                        Continue
                                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                            <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    </button>

                                    <div className="auth-footer">
                                        <p>Already have an account? <Link to="/login" className="auth-link">Sign in</Link></p>
                                    </div>
                                </div>
                            )}

                            {/* Step 2: Personal Information */}
                            {currentStep === 2 && selectedRole === 'patient' && (
                                <div className="step-content fade-in">
                                    <div className="auth-header">
                                        <h1 className="auth-title">Personal Information</h1>
                                        <p className="auth-subtitle">Tell us about yourself</p>
                                    </div>

                                    <div className="form-grid">
                                        <div className="form-group">
                                            <label htmlFor="firstName" className="form-label">First Name *</label>
                                            <input
                                                type="text"
                                                id="firstName"
                                                name="firstName"
                                                className="form-input"
                                                placeholder="John"
                                                value={formData.firstName}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="lastName" className="form-label">Last Name *</label>
                                            <input
                                                type="text"
                                                id="lastName"
                                                name="lastName"
                                                className="form-input"
                                                placeholder="Doe"
                                                value={formData.lastName}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="age" className="form-label">Age *</label>
                                            <input
                                                type="number"
                                                id="age"
                                                name="age"
                                                className="form-input"
                                                placeholder="35"
                                                value={formData.age}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="sex" className="form-label">Sex *</label>
                                            <select
                                                id="sex"
                                                name="sex"
                                                className="form-input form-select"
                                                value={formData.sex}
                                                onChange={handleChange}
                                                required
                                            >
                                                <option value="">Select sex</option>
                                                <option value="male">Male</option>
                                                <option value="female">Female</option>
                                            </select>
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="email" className="form-label">Email Address *</label>
                                            <input
                                                type="email"
                                                id="email"
                                                name="email"
                                                className="form-input"
                                                placeholder="you@example.com"
                                                value={formData.email}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="phone" className="form-label">Phone Number *</label>
                                            <input
                                                type="tel"
                                                id="phone"
                                                name="phone"
                                                className="form-input"
                                                placeholder="+1 (555) 000-0000"
                                                value={formData.phone}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="occupation" className="form-label">Occupation</label>
                                            <input
                                                type="text"
                                                id="occupation"
                                                name="occupation"
                                                className="form-input"
                                                placeholder="Software Engineer"
                                                value={formData.occupation}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="maritalStatus" className="form-label">Marital Status</label>
                                            <select
                                                id="maritalStatus"
                                                name="maritalStatus"
                                                className="form-input form-select"
                                                value={formData.maritalStatus}
                                                onChange={handleChange}
                                            >
                                                <option value="">Select status</option>
                                                <option value="single">Single</option>
                                                <option value="married">Married</option>
                                                <option value="divorced">Divorced</option>
                                                <option value="widowed">Widowed</option>
                                            </select>
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="specialHabits" className="form-label">Special Habits (Smoking, Alcohol, etc.)</label>
                                            <input
                                                type="text"
                                                id="specialHabits"
                                                name="specialHabits"
                                                className="form-input"
                                                placeholder="e.g., Non-smoker, Occasional drinker"
                                                value={formData.specialHabits}
                                                onChange={handleChange}
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="bloodType" className="form-label">Blood Type</label>
                                            <select
                                                id="bloodType"
                                                name="bloodType"
                                                className="form-input form-select"
                                                value={formData.bloodType}
                                                onChange={handleChange}
                                            >
                                                <option value="">Select blood type</option>
                                                <option value="A+">A+</option>
                                                <option value="A-">A-</option>
                                                <option value="B+">B+</option>
                                                <option value="B-">B-</option>
                                                <option value="AB+">AB+</option>
                                                <option value="AB-">AB-</option>
                                                <option value="O+">O+</option>
                                                <option value="O-">O-</option>
                                            </select>
                                        </div>

                                        <div className="form-group">
                                            <div style={{ height: '1px' }}></div>
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="password" className="form-label">Password *</label>
                                            <input
                                                type="password"
                                                id="password"
                                                name="password"
                                                className="form-input"
                                                placeholder="Create a strong password"
                                                value={formData.password}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="confirmPassword" className="form-label">Confirm Password *</label>
                                            <input
                                                type="password"
                                                id="confirmPassword"
                                                name="confirmPassword"
                                                className="form-input"
                                                placeholder="Re-enter your password"
                                                value={formData.confirmPassword}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div className="step-buttons">
                                        <button type="button" onClick={prevStep} className="btn btn-secondary">
                                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                <path d="M13 17L6 10L13 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                            Back
                                        </button>
                                        <button type="button" onClick={nextStep} className="btn btn-primary">
                                            Continue
                                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Step 2: Doctor Information */}
                            {currentStep === 2 && selectedRole === 'doctor' && (
                                <div className="step-content fade-in">
                                    <div className="auth-header">
                                        <h1 className="auth-title">Professional Information</h1>
                                        <p className="auth-subtitle">Verify your medical credentials</p>
                                    </div>

                                    <div className="form-grid">
                                        <div className="form-group">
                                            <label htmlFor="doctorFirstName" className="form-label">First Name *</label>
                                            <input
                                                type="text"
                                                id="doctorFirstName"
                                                name="firstName"
                                                className="form-input"
                                                placeholder="Dr. John"
                                                value={formData.firstName}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="doctorLastName" className="form-label">Last Name *</label>
                                            <input
                                                type="text"
                                                id="doctorLastName"
                                                name="lastName"
                                                className="form-input"
                                                placeholder="Smith"
                                                value={formData.lastName}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="doctorEmail" className="form-label">Professional Email *</label>
                                            <input
                                                type="email"
                                                id="doctorEmail"
                                                name="email"
                                                className="form-input"
                                                placeholder="dr.smith@hospital.com"
                                                value={formData.email}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label className="form-label">Primary Specialty *</label>
                                            <div className="disease-grid" style={{ marginTop: '0.5rem' }}>
                                                {doctorSpecialties.map(spec => (
                                                    <div
                                                        key={spec.id}
                                                        className={`disease-card ${formData.specialty === spec.id ? 'selected' : ''}`}
                                                        onClick={() => setFormData(prev => ({ ...prev, specialty: spec.id }))}
                                                        style={{ padding: '1.25rem' }}
                                                    >
                                                        <div className="disease-icon">{spec.icon}</div>
                                                        <div className="disease-info">
                                                            <div className="disease-name">{spec.name}</div>
                                                            <div className="disease-desc" style={{ fontSize: '0.75rem' }}>{spec.description}</div>
                                                        </div>
                                                        {formData.specialty === spec.id && (
                                                            <div className="disease-check">
                                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                                                    <path d="M5 13L9 17L19 7" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                                                                </svg>
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="hospital" className="form-label">Hospital/Clinic *</label>
                                            <input
                                                type="text"
                                                id="hospital"
                                                name="hospital"
                                                className="form-input"
                                                placeholder="City General Hospital"
                                                value={formData.hospital}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="clinicAddress" className="form-label">Clinic / Hospital Address *</label>
                                            <input
                                                type="text"
                                                id="clinicAddress"
                                                name="clinicAddress"
                                                className="form-input"
                                                placeholder="123 Medical Way, Health City"
                                                value={formData.clinicAddress}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="yearsExperience" className="form-label">Years of Experience *</label>
                                            <input
                                                type="number"
                                                id="yearsExperience"
                                                name="yearsExperience"
                                                className="form-input"
                                                placeholder="10"
                                                value={formData.yearsExperience}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="licenseNumber" className="form-label">Medical License Number *</label>
                                            <input
                                                type="text"
                                                id="licenseNumber"
                                                name="licenseNumber"
                                                className="form-input"
                                                placeholder="ML123456"
                                                value={formData.licenseNumber}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="bio" className="form-label">Professional Bio</label>
                                            <textarea
                                                id="bio"
                                                name="bio"
                                                className="form-input"
                                                placeholder="Briefly describe your medical background and expertise..."
                                                value={formData.bio}
                                                onChange={handleChange}
                                                rows="3"
                                                style={{ resize: 'none' }}
                                            ></textarea>
                                        </div>

                                        <div className="form-group">
                                            <label htmlFor="doctorPhone" className="form-label">Phone Number *</label>
                                            <input
                                                type="tel"
                                                id="doctorPhone"
                                                name="phone"
                                                className="form-input"
                                                placeholder="+1 (555) 000-0000"
                                                value={formData.phone}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="doctorPassword" className="form-label">Password *</label>
                                            <input
                                                type="password"
                                                id="doctorPassword"
                                                name="password"
                                                className="form-input"
                                                placeholder="Create a strong password"
                                                value={formData.password}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>

                                        <div className="form-group full-width">
                                            <label htmlFor="doctorConfirmPassword" className="form-label">Confirm Password *</label>
                                            <input
                                                type="password"
                                                id="doctorConfirmPassword"
                                                name="confirmPassword"
                                                className="form-input"
                                                placeholder="Re-enter your password"
                                                value={formData.confirmPassword}
                                                onChange={handleChange}
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div className="step-buttons">
                                        <button type="button" onClick={prevStep} className="btn btn-secondary">
                                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                <path d="M13 17L6 10L13 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                            Back
                                        </button>
                                        <button type="submit" className="btn btn-primary" disabled={loading}>
                                            {loading ? 'Creating Account...' : 'Create Account'}
                                            {!loading && (
                                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                    <path d="M5 10L8 13L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Step 3: Medical History (Patients Only) */}
                            {currentStep === 3 && selectedRole === 'patient' && (
                                <div className="step-content fade-in">
                                    <div className="auth-header">
                                        <h1 className="auth-title">Medical History</h1>
                                        <p className="auth-subtitle">Select your conditions and provide details</p>
                                    </div>

                                    {/* Disease Selection */}
                                    <div className="disease-selection">
                                        <h3 className="section-title">Do you have any of these conditions?</h3>
                                        <div className="disease-cards">
                                            {diseases.map(disease => (
                                                <div
                                                    key={disease.id}
                                                    className={`disease-card ${selectedDiseases.includes(disease.id) ? 'selected' : ''}`}
                                                    onClick={() => toggleDisease(disease.id)}
                                                >
                                                    <span className="disease-icon">{disease.icon}</span>
                                                    <div className="disease-info">
                                                        <span className="disease-name">{disease.name}</span>
                                                        <p className="disease-description">{disease.description}</p>
                                                    </div>
                                                    {selectedDiseases.includes(disease.id) && (
                                                        <div className="disease-check">✓</div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Disease-Specific Details */}
                                    {selectedDiseases.includes('diabetes') && (
                                        <div className="disease-details">
                                            <h3 className="section-title">🩸 Diabetes - Complete Medical Profile</h3>
                                            <p className="section-subtitle">Help us build your accurate Digital Twin</p>

                                            <div className="form-grid">
                                                <div className="form-group">
                                                    <label htmlFor="diabetesType" className="form-label">Diabetes Type *</label>
                                                    <select
                                                        id="diabetesType"
                                                        name="diabetesType"
                                                        className="form-input form-select"
                                                        value={formData.diabetesType}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select type</option>
                                                        <option value="type1">Type 1</option>
                                                        <option value="type2">Type 2</option>
                                                        <option value="gestational">Gestational</option>
                                                        <option value="prediabetes">Prediabetes</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesDiagnosisYear" className="form-label">Year of Diagnosis *</label>
                                                    <input
                                                        type="number"
                                                        id="diabetesDiagnosisYear"
                                                        name="diabetesDiagnosisYear"
                                                        className="form-input"
                                                        placeholder="2020"
                                                        value={formData.diabetesDiagnosisYear}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesLastHbA1c" className="form-label">Latest HbA1c (%) *</label>
                                                    <input
                                                        type="number"
                                                        step="0.1"
                                                        id="diabetesLastHbA1c"
                                                        name="diabetesLastHbA1c"
                                                        className="form-input"
                                                        placeholder="6.5"
                                                        value={formData.diabetesLastHbA1c}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesLastFBS" className="form-label">Latest Fasting Blood Sugar (mg/dL)</label>
                                                    <input
                                                        type="number"
                                                        id="diabetesLastFBS"
                                                        name="diabetesLastFBS"
                                                        className="form-input"
                                                        placeholder="120"
                                                        value={formData.diabetesLastFBS}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group full-width">
                                                    <label htmlFor="diabetesCurrentMedications" className="form-label">Current Diabetes Medications</label>
                                                    <input
                                                        type="text"
                                                        id="diabetesCurrentMedications"
                                                        name="diabetesCurrentMedications"
                                                        className="form-input"
                                                        placeholder="e.g., Metformin 500mg, Glimepiride 2mg"
                                                        value={formData.diabetesCurrentMedications}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesInsulinUsage" className="form-label">Insulin Usage</label>
                                                    <select
                                                        id="diabetesInsulinUsage"
                                                        name="diabetesInsulinUsage"
                                                        className="form-input form-select"
                                                        value={formData.diabetesInsulinUsage}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select</option>
                                                        <option value="none">No Insulin</option>
                                                        <option value="basal">Basal Insulin Only</option>
                                                        <option value="bolus">Bolus Insulin Only</option>
                                                        <option value="both">Both Basal & Bolus</option>
                                                        <option value="pump">Insulin Pump</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesInsulinDose" className="form-label">Total Daily Insulin (Units)</label>
                                                    <input
                                                        type="number"
                                                        id="diabetesInsulinDose"
                                                        name="diabetesInsulinDose"
                                                        className="form-input"
                                                        placeholder="40"
                                                        value={formData.diabetesInsulinDose}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesBloodSugarMonitoring" className="form-label">Blood Sugar Monitoring Frequency</label>
                                                    <select
                                                        id="diabetesBloodSugarMonitoring"
                                                        name="diabetesBloodSugarMonitoring"
                                                        className="form-input form-select"
                                                        value={formData.diabetesBloodSugarMonitoring}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select frequency</option>
                                                        <option value="never">Never/Rarely</option>
                                                        <option value="weekly">Weekly</option>
                                                        <option value="daily">1-2 times daily</option>
                                                        <option value="multiple">3-4 times daily</option>
                                                        <option value="cgm">Continuous Glucose Monitor</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesHypoglycemiaFrequency" className="form-label">Low Blood Sugar Episodes (per month)</label>
                                                    <select
                                                        id="diabetesHypoglycemiaFrequency"
                                                        name="diabetesHypoglycemiaFrequency"
                                                        className="form-input form-select"
                                                        value={formData.diabetesHypoglycemiaFrequency}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select</option>
                                                        <option value="none">None</option>
                                                        <option value="rare">1-2 times</option>
                                                        <option value="occasional">3-5 times</option>
                                                        <option value="frequent">More than 5 times</option>
                                                    </select>
                                                </div>

                                                <div className="form-group full-width">
                                                    <label htmlFor="diabetesComplications" className="form-label">Diabetes Complications (if any)</label>
                                                    <input
                                                        type="text"
                                                        id="diabetesComplications"
                                                        name="diabetesComplications"
                                                        className="form-input"
                                                        placeholder="e.g., Neuropathy, Retinopathy, Nephropathy, None"
                                                        value={formData.diabetesComplications}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesDietPlan" className="form-label">Current Diet Plan</label>
                                                    <select
                                                        id="diabetesDietPlan"
                                                        name="diabetesDietPlan"
                                                        className="form-input form-select"
                                                        value={formData.diabetesDietPlan}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select</option>
                                                        <option value="none">No Specific Diet</option>
                                                        <option value="diabetic">Diabetic Diet Plan</option>
                                                        <option value="low-carb">Low Carb</option>
                                                        <option value="keto">Ketogenic</option>
                                                        <option value="mediterranean">Mediterranean</option>
                                                        <option value="counting">Carb Counting</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="diabetesExerciseRoutine" className="form-label">Exercise Frequency</label>
                                                    <select
                                                        id="diabetesExerciseRoutine"
                                                        name="diabetesExerciseRoutine"
                                                        className="form-input form-select"
                                                        value={formData.diabetesExerciseRoutine}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select</option>
                                                        <option value="sedentary">Sedentary/Minimal</option>
                                                        <option value="light">Light (1-2 days/week)</option>
                                                        <option value="moderate">Moderate (3-4 days/week)</option>
                                                        <option value="active">Active (5+ days/week)</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {selectedDiseases.includes('copd') && (
                                        <div className="disease-details">
                                            <h3 className="section-title">🫁 COPD Details</h3>
                                            <div className="form-grid">
                                                <div className="form-group">
                                                    <label htmlFor="copdSeverity" className="form-label">Severity</label>
                                                    <select
                                                        id="copdSeverity"
                                                        name="copdSeverity"
                                                        className="form-input form-select"
                                                        value={formData.copdSeverity}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select severity</option>
                                                        <option value="mild">Mild</option>
                                                        <option value="moderate">Moderate</option>
                                                        <option value="severe">Severe</option>
                                                        <option value="very-severe">Very Severe</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="copdDiagnosisYear" className="form-label">Year of Diagnosis</label>
                                                    <input
                                                        type="number"
                                                        id="copdDiagnosisYear"
                                                        name="copdDiagnosisYear"
                                                        className="form-input"
                                                        placeholder="2018"
                                                        value={formData.copdDiagnosisYear}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group full-width">
                                                    <label htmlFor="copdLastFEV1" className="form-label">Last FEV1 (%)</label>
                                                    <input
                                                        type="number"
                                                        id="copdLastFEV1"
                                                        name="copdLastFEV1"
                                                        className="form-input"
                                                        placeholder="65"
                                                        value={formData.copdLastFEV1}
                                                        onChange={handleChange}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {selectedDiseases.includes('heartDisease') && (
                                        <div className="disease-details">
                                            <h3 className="section-title">❤️ Heart Disease Details</h3>
                                            <div className="form-grid">
                                                <div className="form-group">
                                                    <label htmlFor="heartDiseaseType" className="form-label">Type</label>
                                                    <select
                                                        id="heartDiseaseType"
                                                        name="heartDiseaseType"
                                                        className="form-input form-select"
                                                        value={formData.heartDiseaseType}
                                                        onChange={handleChange}
                                                    >
                                                        <option value="">Select type</option>
                                                        <option value="cad">Coronary Artery Disease</option>
                                                        <option value="heartFailure">Heart Failure</option>
                                                        <option value="arrhythmia">Arrhythmia</option>
                                                        <option value="valvular">Valvular Disease</option>
                                                    </select>
                                                </div>

                                                <div className="form-group">
                                                    <label htmlFor="heartDiseaseDiagnosisYear" className="form-label">Year of Diagnosis</label>
                                                    <input
                                                        type="number"
                                                        id="heartDiseaseDiagnosisYear"
                                                        name="heartDiseaseDiagnosisYear"
                                                        className="form-input"
                                                        placeholder="2019"
                                                        value={formData.heartDiseaseDiagnosisYear}
                                                        onChange={handleChange}
                                                    />
                                                </div>

                                                <div className="form-group full-width">
                                                    <label htmlFor="heartDiseaseLastEjectionFraction" className="form-label">Last Ejection Fraction (%)</label>
                                                    <input
                                                        type="number"
                                                        id="heartDiseaseLastEjectionFraction"
                                                        name="heartDiseaseLastEjectionFraction"
                                                        className="form-input"
                                                        placeholder="55"
                                                        value={formData.heartDiseaseLastEjectionFraction}
                                                        onChange={handleChange}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <div className="step-buttons">
                                        <button type="button" onClick={prevStep} className="btn btn-secondary">
                                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                <path d="M13 17L6 10L13 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                            Back
                                        </button>
                                        <button type="submit" className="btn btn-primary" disabled={loading}>
                                            {loading ? 'Creating Account...' : 'Create Account'}
                                            {!loading && (
                                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                                    <path d="M5 10L8 13L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Step 4: Success */}
                            {currentStep === 4 && (
                                <div className="step-content success-content fade-in">
                                    <div className="success-icon">
                                        <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                                            <circle cx="40" cy="40" r="38" stroke="url(#success-gradient)" strokeWidth="4" />
                                            <path d="M20 40L32 52L60 24" stroke="url(#success-gradient)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                                            <defs>
                                                <linearGradient id="success-gradient" x1="0" y1="0" x2="80" y2="80">
                                                    <stop offset="0%" stopColor="#D4AF37" />
                                                    <stop offset="100%" stopColor="#E8B4B8" />
                                                </linearGradient>
                                            </defs>
                                        </svg>
                                    </div>
                                    <h1 className="success-title">Welcome to MedTwin!</h1>
                                    <p className="success-description">
                                        Your account has been created successfully. Redirecting you to your dashboard...
                                    </p>
                                    <div className="loading-dots">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            )}
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SignUpPage
