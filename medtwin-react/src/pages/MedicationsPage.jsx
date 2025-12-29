import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { medicationService } from '../services/api'
import './ConsultationPage.css' // Re-use main styles for consistency

const MedicationsPage = () => {
    const [medications, setMedications] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchMeds = async () => {
            try {
                const res = await medicationService.getMedications()
                if (res.ok) {
                    setMedications(res.schedule || [])
                }
            } catch (error) {
                console.error("Failed to fetch meds", error)
            } finally {
                setLoading(false)
            }
        }
        fetchMeds()
    }, [])

    const userData = JSON.parse(localStorage.getItem('patientUser') || localStorage.getItem('user') || '{}')
    const userInitials = userData.firstName ? `${userData.firstName[0]}${userData.lastName ? userData.lastName[0] : ''}` : 'MT'

    return (
        <div className="consultation-container">
            <aside className="dashboard-sidebar">
                <div className="sidebar-logo">
                    <span className="logo-icon">✨</span>
                    <span>MedTwin</span>
                </div>
                <nav className="sidebar-nav">
                    <Link to="/patient/dashboard" className="nav-item">📊 Dashboard</Link>
                    <Link to="/consultation" className="nav-item">👨‍⚕️ Consultations</Link>
                    <Link to="/patient/medications" className="nav-item active">💊 Medications</Link>
                </nav>
                <div className="sidebar-footer">
                    <div className="user-profile-mini">
                        <div className="user-avatar">{userInitials}</div>
                        <div className="user-info-mini">
                            <h4>{userData.firstName} {userData.lastName}</h4>
                        </div>
                    </div>
                </div>
            </aside>

            <main className="consultation-main" style={{ padding: '2rem' }}>
                <h1 style={{ color: 'var(--champagne)', marginBottom: '2rem' }}>My Medications</h1>

                {loading ? (
                    <div style={{ color: 'white' }}>Loading medications...</div>
                ) : medications.length === 0 ? (
                    <div className="report-card">
                        <h3>No Medications Found</h3>
                        <p style={{ color: 'var(--text-secondary)' }}>You haven't added any medications yet. Go to a consultation or use the 'Add Medication' button.</p>
                        <Link to="/consultation" className="btn-submit-med" style={{ display: 'inline-block', marginTop: '1rem', textDecoration: 'none' }}>
                            Go to Consultation
                        </Link>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                        {medications.map((med, idx) => (
                            <div key={idx} className="patient-card">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <h3 style={{ color: 'var(--text-primary)', margin: 0 }}>💊 {med.name}</h3>
                                    <span style={{
                                        background: 'rgba(76, 175, 80, 0.2)',
                                        color: '#4CAF50',
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '100px',
                                        fontSize: '0.8rem'
                                    }}>Active</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">Dosage</span>
                                    <span className="value">{med.dosage}</span>
                                </div>
                                <div className="info-item">
                                    <span className="label">Timing</span>
                                    <span className="value">{med.timing.join(', ')}</span>
                                </div>
                                <div className="info-item" style={{ marginTop: '0.5rem' }}>
                                    <span className="label">Instructions</span>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                                    {med.instructions || "Take as directed."}
                                </p>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}

export default MedicationsPage
