import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../services/api'
import Navbar from '../components/Navbar'
import './LoginPage.css'

const LoginPage = () => {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        remember: false
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showPassword, setShowPassword] = useState(false)

    // Clear old tokens on load to fix redirection loops
    useEffect(() => {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
    }, [])

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            // Check localStorage for signed up user (for demo)
            const savedUser = JSON.parse(localStorage.getItem('user'));

            if (savedUser && savedUser.email === formData.email && savedUser.password === formData.password) {
                // Simulate successful login
                console.log('Mock login successful');
                navigate(savedUser.role === 'patient' ? '/patient/dashboard' : '/doctor/dashboard');
                return;
            }

            // Fallback to real API (will fail if backend is not running)
            const response = await authService.login(formData.email, formData.password)

            // Save tokens for all possible keys to ensure compatibility
            localStorage.setItem('authToken', response.access_token)
            localStorage.setItem('user', JSON.stringify(response.user))

            if (response.user.role === 'patient') {
                localStorage.setItem('patientToken', response.access_token)
                localStorage.setItem('patientUser', JSON.stringify(response.user))
                navigate('/patient/dashboard')
            } else if (response.user.role === 'doctor') {
                localStorage.setItem('doctorToken', response.access_token)
                localStorage.setItem('doctorUser', JSON.stringify(response.user))
                navigate('/doctor/dashboard')
            }
        } catch (err) {
            setError('Login failed. Please check your credentials or sign up first.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">
            <Navbar />

            <div className="auth-container">
                <div className="auth-box">
                    <div className="auth-header">
                        <h1 className="auth-title">Welcome Back</h1>
                        <p className="auth-subtitle">Sign in to your MedTwin account</p>
                    </div>

                    {error && (
                        <div className="error-message">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
                                <path d="M10 6V10M10 14H10.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="email" className="form-label">Email Address</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M3 4L10 11L17 4M3 4L3 16L17 16L17 4L3 4Z" stroke="currentColor" strokeWidth="1.5" />
                                </svg>
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
                        </div>

                        <div className="form-group">
                            <label htmlFor="password" className="form-label">Password</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <rect x="4" y="9" width="12" height="8" rx="1" stroke="currentColor" strokeWidth="1.5" />
                                    <path d="M7 9V6C7 4.34315 8.34315 3 10 3C11.6569 3 13 4.34315 13 6V9" stroke="currentColor" strokeWidth="1.5" />
                                </svg>
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    id="password"
                                    name="password"
                                    className="form-input"
                                    placeholder="Enter your password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowPassword(!showPassword)}
                                >
                                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                        {showPassword ? (
                                            <>
                                                <path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" stroke="currentColor" strokeWidth="1.5" />
                                                <circle cx="10" cy="10" r="3" stroke="currentColor" strokeWidth="1.5" />
                                            </>
                                        ) : (
                                            <>
                                                <path d="M2 2L18 18M9 9C8.5 9.5 8.5 10.5 9 11C9.5 11.5 10.5 11.5 11 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                                <path d="M7 7C5 8 3 9 2 10C3 11 5 13 7 14M13 13C15 12 17 11 18 10C17 9 15 7 13 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                            </>
                                        )}
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div className="form-options">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="remember"
                                    className="checkbox-input"
                                    checked={formData.remember}
                                    onChange={handleChange}
                                />
                                <span className="checkbox-custom"></span>
                                <span className="checkbox-text">Remember me</span>
                            </label>
                            <Link to="/forgot-password" className="forgot-link">Forgot password?</Link>
                        </div>

                        <button type="submit" className="btn btn-primary btn-large btn-full" disabled={loading}>
                            {loading ? 'Signing in...' : 'Sign In'}
                            {!loading && (
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            )}
                        </button>
                    </form>

                    <div className="divider">
                        <span>or continue with</span>
                    </div>

                    <div className="social-login">
                        <button type="button" className="social-btn">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M18 10.2C18 9.5 17.9 9 17.8 8.5H10V11.7H14.5C14.3 12.8 13.6 13.7 12.6 14.3V16.3H15.4C17 14.9 18 12.8 18 10.2Z" fill="#4285F4" />
                                <path d="M10 18C12.4 18 14.4 17.2 15.4 16.3L12.6 14.3C11.8 14.8 10.8 15.1 10 15.1C7.7 15.1 5.8 13.7 5.1 11.8H2.2V13.9C3.2 15.9 6.4 18 10 18Z" fill="#34A853" />
                                <path d="M5.1 11.8C4.9 11.3 4.8 10.7 4.8 10C4.8 9.3 4.9 8.7 5.1 8.2V6.1H2.2C1.4 7.7 1 9.3 1 10C1 10.7 1.4 12.3 2.2 13.9L5.1 11.8Z" fill="#FBBC05" />
                                <path d="M10 4.9C11 4.9 11.9 5.3 12.6 5.9L15.1 3.4C13.4 1.8 11.3 1 10 1C6.4 1 3.2 3.1 2.2 5.1L5.1 7.2C5.8 5.3 7.7 4.9 10 4.9Z" fill="#EA4335" />
                            </svg>
                            Google
                        </button>
                        <button type="button" className="social-btn">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M18.5 10C18.5 5.3 14.7 1.5 10 1.5C5.3 1.5 1.5 5.3 1.5 10C1.5 14.2 4.6 17.7 8.6 18.4V12.5H6.5V10H8.6V8.1C8.6 6 9.9 4.8 11.8 4.8C12.7 4.8 13.6 5 13.6 5V7H12.6C11.6 7 11.3 7.6 11.3 8.3V10H13.5L13.1 12.5H11.3V18.4C15.4 17.7 18.5 14.2 18.5 10Z" fill="#1877F2" />
                            </svg>
                            Facebook
                        </button>
                    </div>

                    <div className="auth-footer">
                        <p>Don't have an account? <Link to="/signup" className="auth-link">Sign up</Link></p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default LoginPage
