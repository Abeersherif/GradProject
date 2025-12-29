import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { agentService, calendarService, medicationService } from '../services/api'
import './ConsultationPage.css'

const ConsultationPage = () => {
    const navigate = useNavigate()
    const [userData, setUserData] = useState(null)
    const [consultationId, setConsultationId] = useState(null)
    const chatEndRef = useRef(null)

    const [messages, setMessages] = useState([
        {
            id: 'welcome',
            sender: 'agent',
            agentName: 'Diagnostic Agent',
            agentIcon: '🔍',
            text: "Hello! I'm your Diagnostic AI Agent. I've reviewed your biometric data and medical history. How are you feeling today? Please describe your symptoms.",
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
    ])

    const [inputValue, setInputValue] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [activeAgent, setActiveAgent] = useState('diagnostic')
    const [isComplete, setIsComplete] = useState(false)
    const [showMedModal, setShowMedModal] = useState(false)
    const [newMed, setNewMed] = useState({ name: '', dosage: '', frequency: 'Daily', timing: '09:00', instructions: '' })

    useEffect(() => {
        const isDoctorView = window.location.pathname.startsWith('/doctor')
        const key = isDoctorView ? 'doctorUser' : 'patientUser'

        const savedUser = localStorage.getItem(key)
        if (!savedUser) {
            // If they are trying to access patient page but were logged in as doctor
            // check if they have the other role token
            const fallbackKey = isDoctorView ? 'patientUser' : 'doctorUser'
            const fallbackUser = localStorage.getItem(fallbackKey)

            if (!fallbackUser && !localStorage.getItem('user')) {
                navigate('/login')
                return
            }

            // If we have a generic 'user', use it only if it matches current expected view
            const genericUserStr = localStorage.getItem('user')
            if (genericUserStr) {
                const genericUser = JSON.parse(genericUserStr)
                if ((isDoctorView && genericUser.role === 'doctor') || (!isDoctorView && genericUser.role === 'patient')) {
                    setUserData(genericUser)
                    return
                }
            }

            navigate('/login')
            return
        }

        const parsedUser = JSON.parse(savedUser)
        setUserData(parsedUser)
    }, [navigate, window.location.pathname])

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isTyping])

    const handleSendMessage = async (text) => {
        if (!text.trim() || isTyping || isComplete) return

        const userMessage = {
            id: Date.now(),
            sender: 'user',
            text: text,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }

        setMessages(prev => [...prev, userMessage])
        setInputValue('')
        setIsTyping(true)

        try {
            let response;
            if (!consultationId) {
                response = await agentService.startConsultation(text)
                setConsultationId(response.consultationId)
            } else {
                response = await agentService.continueConsultation(consultationId, text)
            }

            const agentResponse = {
                id: Date.now() + 1,
                sender: 'agent',
                agentName: 'Diagnostic Agent',
                agentIcon: '🔍',
                text: response.response,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }

            setMessages(prev => [...prev, agentResponse])

            if (response.completed) {
                await runAgentWorkflow(response.consultationId || consultationId)
            }

        } catch (error) {
            console.error("Consultation Error:", error)
            setMessages(prev => [...prev, {
                id: 'error',
                sender: 'agent',
                agentName: 'System',
                agentIcon: '⚠️',
                text: "I'm having trouble connecting to the medical core. Please ensure the backend is running.",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }])
        } finally {
            setIsTyping(false)
        }
    }

    const runAgentWorkflow = async (id) => {
        setIsTyping(true)

        // 1. Handover to Analysis Agent
        setTimeout(async () => {
            setMessages(prev => [...prev, {
                id: 'handover-1',
                sender: 'system',
                text: "🔄 Diagnostic Agent handing over to Analysis & Simulation Agent...",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }])

            try {
                setActiveAgent('analysis')
                const analysisRes = await agentService.performAnalysis(id)

                setMessages(prev => [...prev, {
                    id: 'analysis-result',
                    sender: 'agent',
                    agentName: 'Analysis Agent',
                    agentIcon: '📊',
                    isReport: true,
                    title: 'Medical Analysis Report',
                    condition: analysisRes.analysis.condition,
                    severity: analysisRes.analysis.severity,
                    content: analysisRes.analysis.recommendations,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }])

                // 2. Handover to Planner Agent
                setTimeout(async () => {
                    setMessages(prev => [...prev, {
                        id: 'handover-2',
                        sender: 'system',
                        text: "🔄 Analysis complete. Handing over to Planner Agent for your Care Plan...",
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }])

                    try {
                        setActiveAgent('planner')
                        const planRes = await agentService.createCarePlan(id)

                        setMessages(prev => [...prev, {
                            id: 'plan-result',
                            sender: 'agent',
                            agentName: 'Planner Agent',
                            agentIcon: '📋',
                            isPlan: true,
                            title: 'Personalized Care Plan',
                            plan: planRes.plan,
                            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        }])

                        setIsComplete(true)
                        setIsTyping(false)

                        // 3. Automatic Sync (Notifier Agent)
                        const status = await calendarService.getStatus()
                        if (status.connected) {
                            setTimeout(async () => {
                                setMessages(prev => [...prev, {
                                    id: 'auto-sync',
                                    sender: 'system',
                                    text: "🔄 Plan generated. Notifier Agent is automatically syncing to your Google Calendar...",
                                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                }])

                                try {
                                    const res = await calendarService.syncCarePlan(id)
                                    if (res.success) {
                                        setMessages(prev => [...prev, {
                                            id: 'auto-sync-success',
                                            sender: 'agent',
                                            agentName: 'Notifier Agent',
                                            agentIcon: '🔔',
                                            text: `✅ Your medical reminders have been automatically synced to Google Calendar.`,
                                            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                        }])
                                    }
                                } catch (e) {
                                    console.error("Auto sync failed:", e)
                                }
                            }, 1500)
                        }

                    } catch (err) { console.error(err); setIsTyping(false) }
                }, 2000)

            } catch (err) { console.error(err) }
        }, 1500)
    }

    const handleSyncCalendar = async () => {
        try {
            const status = await calendarService.getStatus()
            if (!status.connected) {
                const auth = await calendarService.getConnectUrl()
                if (auth.authorization_url) {
                    window.open(auth.authorization_url, '_blank')
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        sender: 'system',
                        text: "📅 Please authorize Google Calendar in the new window, then try syncing again.",
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }])
                }
            } else {
                setMessages(prev => [...prev, {
                    id: 'sync-manual',
                    sender: 'system',
                    text: "⏳ Syncing your latest medical updates to Google Calendar...",
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }])

                if (consultationId) {
                    const res = await calendarService.syncCarePlan(consultationId)
                    if (res.success) {
                        setMessages(prev => [...prev, {
                            id: Date.now().toString(),
                            sender: 'agent',
                            agentName: 'Notifier Agent',
                            agentIcon: '🔔',
                            text: `✅ Care plan synced! Created ${res.reminders_created} recurring reminders.`,
                            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                        }])
                    }
                }
            }
        } catch (err) {
            console.error("Sync error:", err)
        }
    }

    const handleAddMedication = async (e) => {
        e.preventDefault()
        try {
            // First check if calendar is connected
            const status = await calendarService.getStatus()
            if (!status.connected) {
                const auth = await calendarService.getConnectUrl()
                if (auth.authorization_url) {
                    window.open(auth.authorization_url, '_blank')
                    setShowMedModal(false)
                    setMessages(prev => [...prev, {
                        id: Date.now().toString(),
                        sender: 'system',
                        text: "⚠️ Google Calendar not connected. Please authorize in the new window first.",
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    }])
                    return
                }
            }

            const res = await medicationService.addMedication({
                ...newMed,
                timing: [newMed.timing]
            })
            if (res.ok) {
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    sender: 'agent',
                    agentName: 'Notifier Agent',
                    agentIcon: '🔔',
                    text: `✅ Added ${newMed.name} to your medications. I've automatically created reminders in your Google Calendar!`,
                    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }])
                setShowMedModal(false)
                setNewMed({ name: '', dosage: '', frequency: 'Daily', timing: '09:00', instructions: '' })
            }
        } catch (err) {
            console.error(err)
        }
    }

    const userInitials = userData?.firstName ? `${userData.firstName[0]}${userData.lastName ? userData.lastName[0] : ''}` : 'MT'

    return (
        <div className="consultation-container">
            <aside className="dashboard-sidebar">
                <div className="sidebar-logo">
                    <span className="logo-icon">✨</span>
                    <span>MedTwin</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/patient/dashboard" className="nav-item">📊 Dashboard</Link>
                    <Link to="/consultation" className="nav-item active">👨‍⚕️ Consultations</Link>
                    <Link to="/patient/medications" className="nav-item">💊 Medications</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-profile-mini">
                        <div className="user-avatar">{userInitials}</div>
                        <div className="user-info-mini">
                            <h4>{userData?.firstName} {userData?.lastName}</h4>
                        </div>
                    </div>
                </div>
            </aside>

            <main className="consultation-main">
                <div className="chat-window">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`chat-message ${msg.sender === 'agent' ? 'message-agent' : msg.sender === 'system' ? 'message-system' : 'message-user'}`}>
                            {msg.sender !== 'system' && (
                                <div className={`message-avatar ${msg.sender === 'agent' ? 'agent-avatar' : 'user-avatar-circle'}`}>
                                    {msg.sender === 'agent' ? msg.agentIcon : userInitials}
                                </div>
                            )}

                            <div className={`message-bubble ${msg.sender === 'agent' ? 'agent-bubble' : msg.sender === 'system' ? 'system-bubble' : 'user-bubble'} ${msg.isReport || msg.isPlan ? 'rich-content' : ''}`}>
                                {msg.agentName && <div className="bubble-agent-name">{msg.agentName}</div>}

                                {msg.isReport ? (
                                    <div className="report-card">
                                        <h3>📊 Medical Analysis</h3>
                                        <div className="analysis-header">
                                            <div className="header-item">
                                                <h4>Condition</h4>
                                                <div className="header-val">{msg.condition || 'General Analysis'}</div>
                                            </div>
                                            <div className="header-item">
                                                <h4>Severity</h4>
                                                <div className="header-val severity-value">
                                                    <div className={`severity-dot ${msg.severity.toLowerCase()}`}></div>
                                                    {msg.severity}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="recommendations-section">
                                            <h4>💊 Recommendations</h4>
                                            <div className="report-text">{msg.content}</div>
                                        </div>
                                    </div>
                                ) : msg.isPlan ? (
                                    <div className="plan-card">
                                        <h3>📋 Treatment Plan</h3>
                                        <div className="plan-subtitle">🎯 Short-Term Plan (1-7 days)</div>
                                        <div className="plan-grid">
                                            <div className="plan-col">
                                                <h4>✓ Daily Actions</h4>
                                                <ul className="plan-list">
                                                    {msg.plan.short_term_plan.daily_actions.map((a, i) => (
                                                        <li key={i} data-icon="✓">{a}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                            <div className="plan-col">
                                                <h4>📊 Monitoring</h4>
                                                <ul className="plan-list">
                                                    {msg.plan.short_term_plan.monitoring?.map((m, i) => (
                                                        <li key={i} data-icon="📊">{m}</li>
                                                    )) || <li data-icon="📊">Monitor vitals daily</li>}
                                                </ul>
                                            </div>
                                            <div className="plan-col">
                                                <h4>⚠️ Red Flags</h4>
                                                <ul className="plan-list">
                                                    {msg.plan.short_term_plan.red_flags?.map((f, i) => (
                                                        <li key={i} data-icon="🚨">{f}</li>
                                                    )) || <li data-icon="🚨">Severe worsening of symptoms</li>}
                                                </ul>
                                            </div>
                                        </div>
                                        <div className="plan-actions">
                                            <button className="btn-sync" onClick={handleSyncCalendar}>
                                                📅 Sync to Google Calendar
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="bubble-text">{msg.text}</div>
                                )}
                                <div className="bubble-time">{msg.time}</div>
                            </div>
                        </div>
                    ))}
                    {isTyping && (
                        <div className="chat-message message-agent">
                            <div className="message-avatar agent-avatar">{activeAgent === 'diagnostic' ? '🔍' : activeAgent === 'analysis' ? '📊' : '📋'}</div>
                            <div className="message-bubble agent-bubble">
                                <div className="loading-dots"><span></span><span></span><span></span></div>
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                <div className="chat-input-container">
                    {!isComplete && (
                        <form className="chat-input-wrapper" onSubmit={(e) => { e.preventDefault(); handleSendMessage(inputValue) }}>
                            <input
                                type="text"
                                className="chat-input"
                                placeholder="Describe how you're feeling..."
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                disabled={isTyping}
                            />
                            <button type="submit" className="btn-send" disabled={isTyping}>🚀</button>
                        </form>
                    )}
                    {isComplete && (
                        <div className="chat-complete">
                            <Link to="/patient/dashboard" className="btn btn-primary">Medical Ticket Generated - Go to Dashboard</Link>
                        </div>
                    )}
                </div>
            </main>

            <aside className="consultation-info">
                <div className="info-section">
                    <h3>Patient Context</h3>
                    <div className="patient-card">
                        <div className="info-item">
                            <span className="label">Blood Type</span>
                            <span className="value">A+</span>
                        </div>
                        <div className="info-item">
                            <span className="label">Conditions</span>
                            <span className="value">{userData?.conditionCategory || 'General Checkup'}</span>
                        </div>
                    </div>
                </div>

                <div className="info-section">
                    <h3>Medical Notifications</h3>
                    <div className="notification-card">
                        <div className="notify-status">
                            <span className="dot active"></span>
                            <span>Notifier Agent Active</span>
                        </div>
                        <p className="notify-desc">Manually add medications to sync with your Google Calendar.</p>
                        <button className="btn-sidebar-notify" onClick={() => setShowMedModal(true)}>
                            ➕ Add Medication
                        </button>
                    </div>
                </div>

                <div className="info-section">
                    <h3>Active Agents</h3>
                    <div className="agent-status-list">
                        <div className={`status-item ${activeAgent === 'diagnostic' ? 'active' : ''}`}>
                            <span className="icon">🔍</span>
                            <div className="details">
                                <strong>Diagnostic AI</strong>
                                <span>Interviewing</span>
                            </div>
                        </div>
                        <div className={`status-item ${activeAgent === 'analysis' ? 'active' : ''}`}>
                            <span className="icon">📊</span>
                            <div className="details">
                                <strong>Analysis Agent</strong>
                                <span>Analyzing Data</span>
                            </div>
                        </div>
                        <div className={`status-item ${activeAgent === 'planner' ? 'active' : ''}`}>
                            <span className="icon">📋</span>
                            <div className="details">
                                <strong>Planner Agent</strong>
                                <span>Generating Plan</span>
                            </div>
                        </div>
                    </div>
                </div>

                {showMedModal && (
                    <div className="modal-overlay">
                        <div className="modal-content med-modal glass-effect">
                            <div className="modal-header">
                                <h3>➕ Add New Medication</h3>
                                <button className="close-btn" onClick={() => setShowMedModal(false)}>×</button>
                            </div>
                            <form className="med-form" onSubmit={handleAddMedication}>
                                <div className="form-group">
                                    <label>Medication Name</label>
                                    <input
                                        type="text"
                                        placeholder="e.g. Aspirin"
                                        required
                                        value={newMed.name}
                                        onChange={(e) => setNewMed({ ...newMed, name: e.target.value })}
                                    />
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Dosage</label>
                                        <input
                                            type="text"
                                            placeholder="e.g. 500mg"
                                            required
                                            value={newMed.dosage}
                                            onChange={(e) => setNewMed({ ...newMed, dosage: e.target.value })}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Daily Time</label>
                                        <input
                                            type="time"
                                            required
                                            value={newMed.timing}
                                            onChange={(e) => setNewMed({ ...newMed, timing: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <label>Instructions</label>
                                    <textarea
                                        placeholder="e.g. Take after breakfast"
                                        value={newMed.instructions}
                                        onChange={(e) => setNewMed({ ...newMed, instructions: e.target.value })}
                                    ></textarea>
                                </div>
                                <button type="submit" className="btn-submit-med">Add and Sync to Calendar</button>
                            </form>
                        </div>
                    </div>
                )}
            </aside>
        </div>
    )
}

export default ConsultationPage
