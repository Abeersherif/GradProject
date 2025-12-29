import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getAllAgents } from '../config/agents'
import './PatientDashboard.css'

const PatientDashboard = () => {
    const agents = getAllAgents()
    const [userData, setUserData] = useState(null)
    const [isVitalsModalOpen, setIsVitalsModalOpen] = useState(false)

    // Main stats state
    const [stats, setStats] = useState([
        { id: 'heartRate', label: 'Heart Rate', value: '72 bpm', trend: '+2%', status: 'normal', icon: '❤️', color: '#e8b4b8' },
        { id: 'sleep', label: 'Sleep Quality', value: '8.5h', trend: '+12%', status: 'improving', icon: '🌙', color: '#6b46c1' },
        { id: 'steps', label: 'Daily Steps', value: '8,432', trend: '-5%', status: 'low', icon: '🚶', color: '#d4af37' },
        { id: 'calories', label: 'Calorie Intake', value: '2,100', trend: 'Stable', status: 'normal', icon: '🥗', color: '#a8b5a0' }
    ])

    // Biometrics state
    const [vitals, setVitals] = useState({
        bloodPressure: '120/80',
        glucose: 95,
        bloodOxygen: 98,
        bmi: 22.4,
        waistToHip: 0.85
    })

    // Form state for the modal
    const [vitalsForm, setVitalsForm] = useState({
        heartRate: '72',
        sleep: '8.5',
        steps: '8432',
        calories: '2100',
        bloodPressure: '120/80',
        glucose: '95',
        bloodOxygen: '98'
    })

    useEffect(() => {
        try {
            const savedUserStr = localStorage.getItem('patientUser')
            if (savedUserStr && savedUserStr !== 'undefined') {
                setUserData(JSON.parse(savedUserStr))
            } else {
                const genericUserStr = localStorage.getItem('user')
                if (genericUserStr) {
                    const genericUser = JSON.parse(genericUserStr)
                    if (genericUser.role === 'patient') {
                        setUserData(genericUser)
                    }
                }
            }
        } catch (err) {
            console.error("Failed to parse user data from localStorage:", err)
        }
    }, [])

    const handleVitalsChange = (e) => {
        const { name, value } = e.target
        setVitalsForm(prev => ({ ...prev, [name]: value }))
    }

    const saveVitals = (e) => {
        e.preventDefault()

        // Update Stats Grid
        setStats(prev => prev.map(stat => {
            if (stat.id === 'heartRate') return { ...stat, value: `${vitalsForm.heartRate} bpm` }
            if (stat.id === 'sleep') return { ...stat, value: `${vitalsForm.sleep}h` }
            if (stat.id === 'steps') return { ...stat, value: vitalsForm.steps.toLocaleString() }
            if (stat.id === 'calories') return { ...stat, value: vitalsForm.calories }
            return stat
        }))

        // Update Biometrics Card
        setVitals(prev => ({
            ...prev,
            bloodPressure: vitalsForm.bloodPressure,
            glucose: parseInt(vitalsForm.glucose),
            bloodOxygen: parseInt(vitalsForm.bloodOxygen)
        }))

        setIsVitalsModalOpen(false)
    }

    const timelineEvents = [
        { id: 1, type: 'consultation', title: 'AI Consultation Completed', description: 'Diagnostic Agent performed initial analysis.', time: '2 hours ago', icon: '🔍' },
        { id: 2, type: 'medication', title: 'Medication Taken', description: 'Metformin 500mg - Morning Dose.', time: '4 hours ago', icon: '💊' },
        { id: 3, type: 'lab', title: 'Lab Results Uploaded', description: 'Blood glucose panel processed.', time: 'Yesterday', icon: '🧪' },
        { id: 4, type: 'analysis', title: 'Weekly Summary Ready', description: 'Analysis Agent compiled your health trends.', time: '2 days ago', icon: '📊' }
    ]

    // Safe initials calculation
    const userInitials = (() => {
        if (!userData) return 'MT'
        if (userData.firstName && userData.lastName) {
            return `${userData.firstName[0]}${userData.lastName[0]}`.toUpperCase()
        }
        if (userData.fullName) {
            const parts = userData.fullName.split(' ')
            if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
            return parts[0][0].toUpperCase()
        }
        if (userData.full_name) {
            const parts = userData.full_name.split(' ')
            if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
            return parts[0][0].toUpperCase()
        }
        return 'MT'
    })()

    // Safe full name calculation
    const fullName = userData?.firstName && userData?.lastName
        ? `${userData.firstName} ${userData.lastName}`
        : (userData?.fullName || userData?.full_name || 'Guest User')

    return (
        <div className="dashboard-container">
            {/* Sidebar */}
            <aside className="dashboard-sidebar">
                <div className="sidebar-logo">
                    <span className="logo-icon">✨</span>
                    <span>MedTwin</span>
                </div>

                <nav className="sidebar-nav">
                    <Link to="/patient/dashboard" className="nav-item active">
                        <span className="nav-icon">📊</span>
                        <span>Dashboard</span>
                    </Link>
                    <Link to="/patient/consultation" className="nav-item">
                        <span className="nav-icon">👨‍⚕️</span>
                        <span>Consultations</span>
                    </Link>
                    <Link to="/patient/medications" className="nav-item">
                        <span className="nav-icon">💊</span>
                        <span>Medications</span>
                    </Link>
                    <Link to="/patient/lab-results" className="nav-item">
                        <span className="nav-icon">🧪</span>
                        <span>Reports</span>
                    </Link>
                    <Link to="/patient/profile" className="nav-item">
                        <span className="nav-icon">👤</span>
                        <span>Profile</span>
                    </Link>
                </nav>

                <div className="sidebar-footer">
                    <div className="user-profile-mini">
                        <div className="user-avatar">{userInitials}</div>
                        <div className="user-info-mini">
                            <h4>{fullName}</h4>
                            <p>ID: {userData?.id || 'MT-0000'}</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="dashboard-main">
                <header className="dashboard-header">
                    <div className="welcome-section">
                        <h1>Welcome back, {userData?.firstName || (fullName.split(' ')[0]) || 'User'}</h1>
                        <p>Your AI agents have processed 12 new data points today.</p>
                    </div>
                    <div className="header-actions">
                        <button className="btn btn-outline" onClick={() => setIsVitalsModalOpen(true)}>
                            <span>➕</span> Input Vitals
                        </button>
                        <Link to="/consultation" className="btn btn-primary">
                            <span>💬</span> New Consultation
                        </Link>
                    </div>
                </header>

                {/* Stats Grid */}
                <section className="stats-grid">
                    {stats.map((stat, index) => (
                        <div key={index} className="stat-card">
                            <div className="stat-header">
                                <div className="stat-icon" style={{ backgroundColor: `${stat.color}15`, color: stat.color }}>
                                    {stat.icon}
                                </div>
                                <span className={`stat-trend ${stat.trend.startsWith('+') ? 'trend-up' : 'trend-down'}`}>
                                    {stat.trend}
                                </span>
                            </div>
                            <div className="stat-value">{stat.value}</div>
                            <div className="stat-label">{stat.label}</div>
                        </div>
                    ))}
                </section>

                {/* AI Agents Hive */}
                <section className="agents-overview">
                    <div className="section-header">
                        <h2 className="section-title">AI Agents Hive</h2>
                        <Link to="/agents" className="btn-link">View All Systems →</Link>
                    </div>
                    <div className="agents-grid">
                        {agents.slice(0, 6).map((agent, index) => (
                            <div key={agent.id} className="agent-mini-card">
                                <div className="agent-icon-small" style={{ color: agent.color }}>
                                    {agent.icon}
                                </div>
                                <div className="agent-info">
                                    <div className="agent-name">
                                        {agent.name}
                                        <span className="agent-status">Active</span>
                                    </div>
                                    <div className="agent-last-log">
                                        {index === 0 ? "Diagnostic analysis ready" :
                                            index === 1 ? "Trends processed" :
                                                "Monitoring steady..."}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <div className="dashboard-grid-bottom">
                    <section className="health-timeline">
                        <h2 className="section-title">Health Timeline</h2>
                        <div className="timeline-list">
                            {timelineEvents.map(event => (
                                <div key={event.id} className="timeline-item">
                                    <div className="timeline-date">{event.icon}</div>
                                    <div className="timeline-content">
                                        <h4>{event.title}</h4>
                                        <p>{event.description}</p>
                                        <div className="timeline-time">{event.time}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <aside className="user-vitals-card">
                        <h2 className="section-title">Biometrics</h2>
                        <div className="vitals-list">
                            <div className="vital-item">
                                <span className="vital-label">Blood Pressure</span>
                                <span className="vital-value">{vitals.bloodPressure} mmHg</span>
                            </div>
                            <div className="vital-item">
                                <span className="vital-label">Glucose (Avg)</span>
                                <span className="vital-value">{vitals.glucose} mg/dL</span>
                            </div>
                            <div className="vital-item">
                                <span className="vital-label">Blood Oxygen</span>
                                <span className="vital-value">{vitals.bloodOxygen}%</span>
                            </div>
                            <div className="vital-item">
                                <span className="vital-label">BMI</span>
                                <span className="vital-value">{vitals.bmi}</span>
                            </div>
                        </div>

                        <div style={{ marginTop: '2rem' }}>
                            <h3 style={{ fontSize: '1rem', marginBottom: '1rem' }}>Personal History</h3>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                                <p><strong>Conditions:</strong> {
                                    userData?.diseases?.length > 0
                                        ? (Array.isArray(userData.diseases) ? userData.diseases.join(', ') : userData.diseases)
                                        : (userData?.conditionCategory || 'None reported')
                                }</p>
                                <p><strong>Age:</strong> {userData?.age || 'N/A'}</p>
                                <p><strong>Sex:</strong> {userData?.sex || userData?.gender || 'N/A'}</p>
                                <p><strong>Blood Type:</strong> {userData?.bloodType || 'N/A'}</p>
                                <p><strong>Occupation:</strong> {userData?.occupation || 'N/A'}</p>
                            </div>
                        </div>
                    </aside>
                </div>

                {/* Vitals Input Modal */}
                {isVitalsModalOpen && (
                    <div className="modal-overlay">
                        <div className="modal-content fadeIn">
                            <button className="modal-close" onClick={() => setIsVitalsModalOpen(false)}>&times;</button>
                            <h2 className="modal-title">Log New Vitals</h2>

                            <form onSubmit={saveVitals} className="vitals-form">
                                <div className="form-group">
                                    <label className="form-label">Heart Rate (bpm)</label>
                                    <input
                                        type="number"
                                        name="heartRate"
                                        className="form-input"
                                        value={vitalsForm.heartRate}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Sleep (hours)</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        name="sleep"
                                        className="form-input"
                                        value={vitalsForm.sleep}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Daily Steps</label>
                                    <input
                                        type="number"
                                        name="steps"
                                        className="form-input"
                                        value={vitalsForm.steps}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Calories</label>
                                    <input
                                        type="number"
                                        name="calories"
                                        className="form-input"
                                        value={vitalsForm.calories}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Blood Pressure</label>
                                    <input
                                        type="text"
                                        name="bloodPressure"
                                        className="form-input"
                                        placeholder="120/80"
                                        value={vitalsForm.bloodPressure}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Glucose (mg/dL)</label>
                                    <input
                                        type="number"
                                        name="glucose"
                                        className="form-input"
                                        value={vitalsForm.glucose}
                                        onChange={handleVitalsChange}
                                    />
                                </div>
                                <div className="form-group full-width">
                                    <label className="form-label">Blood Oxygen (%)</label>
                                    <input
                                        type="number"
                                        name="bloodOxygen"
                                        className="form-input"
                                        value={vitalsForm.bloodOxygen}
                                        onChange={handleVitalsChange}
                                    />
                                </div>

                                <div className="form-group full-width">
                                    <button type="submit" className="btn btn-primary btn-full">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}

export default PatientDashboard
