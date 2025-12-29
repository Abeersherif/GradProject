import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

// Pages
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignUpPage from './pages/SignUpPage'
import PatientDashboard from './pages/PatientDashboard'
import DoctorDashboard from './pages/DoctorDashboard'
import ConsultationPage from './pages/ConsultationPage'
import MedicationsPage from './pages/MedicationsPage'
import LabResultsPage from './pages/LabResultsPage'
import ProfilePage from './pages/ProfilePage'
import DigitalTwinPage from './pages/DigitalTwinPage'

// Components
import AnimatedBackground from './components/AnimatedBackground'

import GoogleCallback from './pages/GoogleCallback'

function App() {
    return (
        <Router>
            <div className="app">
                <AnimatedBackground />
                <Routes>
                    {/* Public Routes */}
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route path="/auth/google/callback" element={<GoogleCallback />} />

                    {/* Patient Routes */}
                    <Route path="/patient/dashboard" element={<PatientDashboard />} />
                    <Route path="/consultation" element={<ConsultationPage />} />
                    <Route path="/patient/consultation" element={<ConsultationPage />} />
                    <Route path="/patient/medications" element={<MedicationsPage />} />
                    <Route path="/patient/digital-twin" element={<DigitalTwinPage />} />
                    <Route path="/patient/lab-results" element={<LabResultsPage />} />
                    <Route path="/patient/profile" element={<ProfilePage />} />

                    {/* Doctor Routes */}
                    <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
                    <Route path="/doctor/patients/:patientId" element={<ConsultationPage />} />
                    <Route path="/doctor/profile" element={<ProfilePage />} />
                </Routes>
            </div>
        </Router>
    )
}

export default App
