import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { doctorService } from '../services/api'
import './DoctorDashboard.css'

const DoctorDashboard = () => {
    const [view, setView] = useState('dashboard') // 'dashboard', 'patients'
    const [queue, setQueue] = useState([])
    const [myPatients, setMyPatients] = useState([])
    const [stats, setStats] = useState({ pending_reviews: 0, approved_today: 0, total_patients: 0 })
    const [selectedTicket, setSelectedTicket] = useState(null)
    const [loading, setLoading] = useState(true)
    const [isApproving, setIsApproving] = useState(false)
    const [selectedPatientHistory, setSelectedPatientHistory] = useState(null)
    const [showHistoryModal, setShowHistoryModal] = useState(false)

    const [user, setUser] = useState(null)

    useEffect(() => {
        fetchData()
        const interval = setInterval(fetchData, 15000)

        // Load logged in doctor info
        const savedUserStr = localStorage.getItem('doctorUser')
        if (savedUserStr) {
            setUser(JSON.parse(savedUserStr))
        } else {
            const genericUserStr = localStorage.getItem('user')
            if (genericUserStr) {
                const genericUser = JSON.parse(genericUserStr)
                if (genericUser.role === 'doctor') {
                    setUser(genericUser)
                } else {
                    // navigate to login or similar
                }
            }
        }

        return () => clearInterval(interval)
    }, [])

    const fetchData = async () => {
        try {
            const [queueRes, statsRes] = await Promise.all([
                doctorService.getPatientQueue(),
                doctorService.getDashboard()
            ])
            setQueue(queueRes.queue || [])
            setStats(statsRes.statistics || {})
            setLoading(false)
        } catch (error) {
            console.error("Dashboard Error:", error)
            setLoading(false)
        }
    }

    const loadMyPatients = async () => {
        try {
            const res = await doctorService.getMyPatients()
            setMyPatients(res.patients || [])
        } catch (error) {
            console.error("Error loading patients:", error)
        }
    }

    const handleViewChange = (newView) => {
        setView(newView)
        setSelectedTicket(null)
        if (newView === 'patients') {
            loadMyPatients()
        }
    }

    const handleTicketSelect = async (ticketId) => {
        try {
            const res = await doctorService.getTicket(ticketId)
            setSelectedTicket(res.ticket)
            // Ensure we are in dashboard view when opening a ticket
            if (view !== 'dashboard') setView('dashboard')
        } catch (error) {
            console.error("Error loading ticket", error)
        }
    }

    const handleApprove = async () => {
        if (!selectedTicket) return
        setIsApproving(true)
        try {
            await doctorService.approveTicket(selectedTicket.id, "Approved via Doctor Portal")
            alert("✓ Care Plan Approved & Synced")
            setSelectedTicket(null)
            fetchData() // Refresh queue and stats
            // If they were previously viewing patients, reload that too
            if (view === 'patients') loadMyPatients()
        } catch (error) {
            alert("Approval Failed: " + error.message)
        } finally {
            setIsApproving(false)
        }
    }

    const handleViewHistory = async (patientId) => {
        try {
            // Get token from either key to be safe
            const token = localStorage.getItem('doctorToken') || localStorage.getItem('authToken');

            // Fetch patient's consultation history
            const response = await fetch(`/api/patient/${patientId}/consultations`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) {
                if (response.status === 403 || response.status === 401) {
                    throw new Error("Session expired or unauthorized. Please log in again.");
                }
                const errorData = await response.json();
                throw new Error(errorData.error || "Failed to fetch record");
            }

            const data = await response.json()
            setSelectedPatientHistory(data)
            setShowHistoryModal(true)
        } catch (error) {
            console.error("Error loading patient history:", error)
            alert("Error: " + error.message)
        }
    }

    // -- Sub-components --

    const StatCard = ({ icon, value, label, trend, color, trendClass }) => (
        <div className="stat-card">
            <div className="stat-header">
                <div className="stat-icon" style={{ backgroundColor: `${color}15`, color: color }}>
                    {icon}
                </div>
                <span className={`stat-trend ${trendClass}`}>{trend}</span>
            </div>
            <div className="stat-value">{value}</div>
            <div className="stat-label">{label}</div>
        </div>
    )

    if (loading && !queue.length) {
        return <div className="dashboard-container" style={{ justifyContent: 'center', alignItems: 'center' }}>Loading Workspace...</div>
    }

    return (
        <div className="dashboard-container">
            {/* Sidebar */}
            <aside className="dashboard-sidebar">
                <div className="sidebar-logo">
                    <span className="logo-icon">🩺</span>
                    <span>MedTwin</span>
                </div>

                <nav className="sidebar-nav">
                    <div
                        className={`nav-item ${view === 'dashboard' ? 'active' : ''}`}
                        onClick={() => handleViewChange('dashboard')}
                    >
                        <span className="nav-icon">📊</span>
                        <span>Clinical Board</span>
                    </div>
                    <div
                        className={`nav-item ${view === 'patients' ? 'active' : ''}`}
                        onClick={() => handleViewChange('patients')}
                    >
                        <span className="nav-icon">👥</span>
                        <span>My Patients</span>
                    </div>
                    <div className="nav-item">
                        <span className="nav-icon">📅</span>
                        <span>Schedule</span>
                    </div>
                </nav>

                <div className="sidebar-footer">
                    <div className="user-profile-mini">
                        <div className="user-avatar" style={{ background: 'var(--gradient-blue)' }}>
                            {user ? (
                                (user.fullName || user.full_name || user.name || 'DR')
                                    .trim().split(/\s+/)
                                    .map(n => n[0]).join('').substring(0, 2).toUpperCase()
                            ) : 'DR'}
                        </div>
                        <div className="user-info-mini">
                            <h4>{user ? `Dr. ${(user.fullName || user.full_name || user.name || 'User').split(' ').pop()}` : 'Dr. User'}</h4>
                            <p>{user?.email || 'Cardiology Dept.'}</p>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="dashboard-main">
                <header className="dashboard-header">
                    <div className="welcome-section">
                        <h1>{view === 'dashboard' ? 'Clinician Workspace' : 'My Patients'}</h1>
                        <p>
                            {view === 'dashboard'
                                ? `You have ${stats.pending_reviews} pending cases requiring review today.`
                                : `Manage your cohort of ${myPatients.length} active patients.`
                            }
                        </p>
                    </div>
                    <div className="header-actions">
                        <button className="btn btn-outline" onClick={() => { fetchData(); if (view === 'patients') loadMyPatients(); }}>
                            <span>🔄</span> Refresh
                        </button>
                    </div>
                </header>

                {view === 'dashboard' ? (
                    <>
                        {/* Stats Grid */}
                        <section className="stats-grid">
                            <StatCard
                                icon="📋" value={stats.pending_reviews} label="Pending Reviews" trend="Action Req" color="#ffa500" trendClass="trend-down"
                            />
                            <StatCard
                                icon="✅" value={stats.approved_today} label="Processed Today" trend="+12%" color="#4caf50" trendClass="trend-up"
                            />
                            <StatCard
                                icon="👥" value={stats.total_patients} label="Total Patients" trend="Active" color="#2196f3" trendClass="trend-up"
                            />
                        </section>

                        <div className="dashboard-grid-bottom">

                            {/* LEFT: Queue */}
                            <aside className="queue-section">
                                <div className="section-header">
                                    <h2 className="section-title">Live Patient Queue</h2>
                                    <span className="badge badge-LOW">{queue.length} Wait</span>
                                </div>

                                <div className="queue-list">
                                    {queue.length === 0 ? (
                                        <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', textAlign: 'center', padding: '2rem' }}>
                                            All caught up! No pending tickets.
                                        </p>
                                    ) : (
                                        queue.map(t => (
                                            <div
                                                key={t.ticket_id}
                                                onClick={() => handleTicketSelect(t.ticket_id)}
                                                className={`queue-item ${selectedTicket?.id === t.ticket_id ? 'selected' : ''}`}
                                            >
                                                <div className="queue-patient-info">
                                                    <h4>{t.patient.name}</h4>
                                                    <p>{t.summary.chief_complaint}</p>
                                                </div>
                                                <span className={`badge badge-${t.summary.urgency || 'LOW'}`}>
                                                    {t.summary.urgency || 'MED'}
                                                </span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </aside>

                            {/* RIGHT: Detail View */}
                            <section className="ticket-detail-container" style={{ flex: 2 }}>
                                {!selectedTicket ? (
                                    <div className="ticket-detail" style={{ textAlign: 'center', padding: '4rem' }}>
                                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏥</div>
                                        <h3>Ready for Review</h3>
                                        <p style={{ color: 'var(--text-secondary)' }}>Select a patient from the queue to view AI analysis.</p>
                                    </div>
                                ) : (
                                    <div className="ticket-detail">
                                        <div className="detail-header">
                                            <div>
                                                <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{selectedTicket.patient.name}</h2>
                                                <p style={{ color: 'var(--text-secondary)' }}>
                                                    ID: {selectedTicket.patient.id} • {selectedTicket.patient.gender} • {selectedTicket.patient.condition_category}
                                                </p>
                                            </div>
                                            <span className={`badge badge-${selectedTicket.medical_ticket.summary.urgency}`} style={{ fontSize: '1rem' }}>
                                                {selectedTicket.medical_ticket.summary.urgency} PRIORITY
                                            </span>
                                        </div>

                                        <div className="detail-grid">
                                            <div className="left-col">
                                                <div className="clinical-section">
                                                    <h3>🔍 Clinical Analysis</h3>
                                                    <div className="info-box">
                                                        <p><strong>Chief Complaint:</strong> {selectedTicket.medical_ticket.summary.chief_complaint}</p>
                                                        <br />
                                                        <p><strong>AI Condition Assessment:</strong> {selectedTicket.medical_ticket.ai_analysis.condition}</p>
                                                        <br />
                                                        <p><strong>Recommendation:</strong> {selectedTicket.medical_ticket.ai_analysis.recommendations}</p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="right-col">
                                                <div className="clinical-section">
                                                    <h3>📝 AI Proposed Plan</h3>
                                                    <div className="plan-actions">
                                                        {selectedTicket.medical_ticket.proposed_care_plan.short_term.daily_actions.map((action, i) => (
                                                            <div key={i} className="action-item">
                                                                <span className="action-number">{i + 1}</span>
                                                                <span>{action}</span>
                                                            </div>
                                                        ))}

                                                        <div style={{ marginTop: '2rem' }}>
                                                            <button
                                                                className="btn btn-primary btn-full"
                                                                onClick={handleApprove}
                                                                disabled={isApproving}
                                                                style={{ width: '100%', justifyContent: 'center' }}
                                                            >
                                                                {isApproving ? 'Syncing...' : '✓ Approve & Sync'}
                                                            </button>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </section>
                        </div>
                    </>
                ) : (
                    // MY PATIENTS VIEW
                    <div className="patients-view">
                        <div className="stats-grid">
                            <StatCard icon="👥" value={myPatients.length} label="Total Patients" trend="Active" color="#2196f3" trendClass="trend-up" />
                            <StatCard icon="⚠️" value="0" label="Critical Alerts" trend="Stable" color="#ffa500" trendClass="trend-up" />
                            <StatCard icon="📅" value="Today" label="Next Follow-up" trend="Scheduled" color="#4caf50" trendClass="trend-up" />
                        </div>

                        <div className="table-container">
                            <table className="patient-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Medical Summary</th>
                                        <th>Clinical Profile</th>
                                        <th>Last Review</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {myPatients.length === 0 ? (
                                        <tr>
                                            <td colSpan="5" style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
                                                No patients assigned to your care yet.
                                            </td>
                                        </tr>
                                    ) : (
                                        myPatients.map(p => (
                                            <tr key={p.id}>
                                                <td>
                                                    <div className="patient-main-info">
                                                        <span className="patient-name">{p.name}</span>
                                                        <span className="patient-meta">{p.gender}, {p.age} yrs</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="med-info-summary">
                                                        {p.medical_summary && p.medical_summary.length > 0 ? (
                                                            p.medical_summary.map((med, idx) => (
                                                                <div key={idx} className="med-detail-item">
                                                                    • {med}
                                                                </div>
                                                            ))
                                                        ) : (
                                                            <span className="text-muted" style={{ fontStyle: 'italic', fontSize: '0.8rem' }}>No pre-existing conditions reported.</span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td>
                                                    <div className="medical-tags">
                                                        <span className="med-tag">🩸 {p.blood_type || 'N/A'}</span>
                                                    </div>
                                                </td>
                                                <td>
                                                    <span className="last-visit-cell">{p.last_visit}</span>
                                                </td>
                                                <td>
                                                    <button
                                                        onClick={() => handleViewHistory(p.id)}
                                                        className="btn btn-outline btn-small"
                                                        style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                                                    >
                                                        Clinical History
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </main>

            {/* PATIENT HISTORY MODAL */}
            {showHistoryModal && (
                <div className="modal-overlay" onClick={() => setShowHistoryModal(false)}>
                    <div className="modal-content history-modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '900px', width: '90%', maxHeight: '85vh', overflow: 'auto' }}>
                        <div className="modal-header">
                            <h2>Clinical History & Consultations</h2>
                            <button className="close-btn" onClick={() => setShowHistoryModal(false)}>×</button>
                        </div>
                        <div className="modal-body p-6">
                            {!selectedPatientHistory || selectedPatientHistory.consultations?.length === 0 ? (
                                <p className="text-center text-gray-500 py-10">No consultation history found for this patient.</p>
                            ) : (
                                <div className="space-y-6">
                                    {selectedPatientHistory.consultations.map(c => (
                                        <div key={c.id} className="bg-[#1a1e2b] rounded-xl p-6 border border-gray-800 shadow-xl">
                                            <div className="flex justify-between items-center mb-4 border-b border-gray-800 pb-3">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-cyan-400 font-bold">CASE #{c.id}</span>
                                                    <span className="text-xs text-gray-500">{new Date(c.created_at).toLocaleString()}</span>
                                                </div>
                                                <span className={`badge badge-${c.status === 'completed' ? 'LOW' : 'HIGH'}`}>
                                                    {c.status.toUpperCase()}
                                                </span>
                                            </div>

                                            <div className="grid md:grid-cols-2 gap-6">
                                                <div className="space-y-4">
                                                    <div>
                                                        <h4 className="text-xs uppercase text-gray-500 mb-2">AI Analysis Result</h4>
                                                        <div className="text-sm p-3 bg-[#131620] rounded border border-gray-700 text-gray-300">
                                                            {c.analysis_result ? (
                                                                <div className="space-y-2">
                                                                    <div className="flex justify-between">
                                                                        <span className="font-medium text-cyan-400">Diagnosis:</span>
                                                                        <span>{typeof c.analysis_result === 'string' ? JSON.parse(c.analysis_result).condition : c.analysis_result.condition}</span>
                                                                    </div>
                                                                    <div className="flex justify-between">
                                                                        <span className="font-medium text-cyan-400">Severity:</span>
                                                                        <span>{typeof c.analysis_result === 'string' ? JSON.parse(c.analysis_result).severity : c.analysis_result.severity}</span>
                                                                    </div>
                                                                    <div className="text-xs mt-2 text-gray-400">
                                                                        {typeof c.analysis_result === 'string' ? JSON.parse(c.analysis_result).recommendations : c.analysis_result.recommendations}
                                                                    </div>
                                                                </div>
                                                            ) : 'No analysis available'}
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <h4 className="text-xs uppercase text-gray-500 mb-2">Patient Collected Data</h4>
                                                        <div className="text-xs p-3 bg-[#131620] rounded border border-gray-700 text-gray-400 max-h-[150px] overflow-y-auto">
                                                            <pre className="whitespace-pre-wrap">
                                                                {JSON.stringify(c.collected_data, null, 2)}
                                                            </pre>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="space-y-4">
                                                    <div>
                                                        <h4 className="text-xs uppercase text-gray-500 mb-2">Digital Twin Care Plan</h4>
                                                        <div className="text-sm p-3 bg-[#131620] rounded border border-gray-700 text-gray-300">
                                                            {c.care_plan ? (
                                                                <div className="space-y-3">
                                                                    <p className="text-cyan-300 font-medium">Proposed Plan:</p>
                                                                    <div className="text-xs whitespace-pre-wrap">{typeof c.care_plan === 'string' ? c.care_plan : JSON.stringify(c.care_plan, null, 2)}</div>
                                                                </div>
                                                            ) : 'Care plan not yet generated'}
                                                        </div>
                                                    </div>

                                                    <div className="flex gap-2 mt-4">
                                                        <button className="btn btn-outline btn-small" style={{ flex: 1 }}>📄 Export Report</button>
                                                        <button className="btn btn-primary btn-small" style={{ flex: 1 }}>🔍 Open Details</button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default DoctorDashboard
