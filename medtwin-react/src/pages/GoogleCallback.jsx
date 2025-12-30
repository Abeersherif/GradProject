import { useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

const GoogleCallback = () => {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()

    useEffect(() => {
        const handleCallback = async () => {
            const code = searchParams.get('code')
            if (code) {
                try {
                    // Send code to backend to exchange for token
                    // The backend route is /api/calendar/callback but we can redirect or call it
                    window.location.href = `https://medtwin.onrender.com/api/calendar/callback?code=${code}`
                } catch (error) {
                    console.error("Auth failed:", error)
                    navigate('/consultation')
                }
            }
        }
        handleCallback()
    }, [searchParams, navigate])

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            background: '#1a1a1a',
            flexDirection: 'column',
            gap: '1rem'
        }}>
            <div className="spinner">✨</div>
            <h2>Connecting to Google Calendar...</h2>
            <p>Please wait while we sync your medical agent.</p>
        </div>
    )
}

export default GoogleCallback
