import { Link } from 'react-router-dom'
import './Navbar.css'

const Navbar = () => {
    return (
        <nav className="navbar">
            <div className="nav-container">
                {/* Logo */}
                <Link to="/" className="logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="logo-icon">
                        <path d="M12 2L12 22M2 12L22 12" stroke="url(#nav-logo-gradient)" strokeWidth="2" strokeLinecap="round" />
                        <circle cx="12" cy="12" r="5" stroke="url(#nav-logo-gradient)" strokeWidth="1.5" fill="none" />
                        <defs>
                            <linearGradient id="nav-logo-gradient" x1="0" y1="0" x2="24" y2="24">
                                <stop offset="0%" stopColor="#D4AF37" />
                                <stop offset="100%" stopColor="#E8B4B8" />
                            </linearGradient>
                        </defs>
                    </svg>
                    <span className="logo-text">MedTwin</span>
                </Link>

                {/* Navigation Links */}
                <ul className="nav-links">
                    <li><a href="#features">Features</a></li>
                    <li><a href="#how-it-works">How It Works</a></li>
                    <li><a href="#about">About</a></li>
                </ul>

                {/* Auth Buttons */}
                <div className="nav-auth">
                    <Link to="/login" className="nav-login">Login</Link>
                    <Link to="/signup" className="btn btn-primary">Get Started</Link>
                </div>
            </div>
        </nav>
    )
}

export default Navbar
