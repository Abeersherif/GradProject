import { Link } from 'react-router-dom'
import { getAllAgents } from '../config/agents'
import Navbar from '../components/Navbar'
import './LandingPage.css'

const LandingPage = () => {
    const agents = getAllAgents()

    return (
        <div className="landing-page">
            <Navbar />

            {/* Hero Section */}
            <section className="hero">
                <div className="container hero-container">
                    <div className="hero-content fade-in-up">
                        <div className="hero-badge">
                            <span className="badge-dot"></span>
                            AI-Powered Healthcare
                        </div>
                        <h1 className="hero-title">
                            Your Health,<br />
                            <span className="gradient-text">Intelligently</span><br />
                            Monitored
                        </h1>
                        <p className="hero-description">
                            Experience the future of personalized healthcare with MedTwin's revolutionary digital twin technology.
                            Nine specialized AI agents working in harmony to keep you healthy, safe, and informed.
                        </p>
                        <div className="hero-buttons">
                            <Link to="/signup" className="btn btn-primary btn-large">
                                Start Your Journey
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            </Link>
                            <a href="#how-it-works" className="btn btn-outline btn-large">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
                                    <path d="M10 6L10 10L13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                                Watch Demo
                            </a>
                        </div>
                        <div className="hero-stats">
                            <div className="stat">
                                <div className="stat-number">9</div>
                                <div className="stat-label">AI Agents</div>
                            </div>
                            <div className="stat">
                                <div className="stat-number">24/7</div>
                                <div className="stat-label">Monitoring</div>
                            </div>
                            <div className="stat">
                                <div className="stat-number">99.9%</div>
                                <div className="stat-label">Accuracy</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="section features">
                <div className="container">
                    <div className="section-header">
                        <h2 className="section-title">
                            Nine AI Agents,<br />
                            <span className="gradient-text">One Mission</span>
                        </h2>
                        <p className="section-description">
                            Our specialized AI agents work collaboratively to provide comprehensive, personalized healthcare monitoring and support.
                        </p>
                    </div>

                    <div className="features-grid">
                        {agents.map((agent, index) => (
                            <div
                                key={agent.id}
                                className={`feature-card fade-in-up ${agent.id === 'coordinator' ? 'feature-card-highlight' : ''}`}
                                style={{ animationDelay: `${index * 0.1}s` }}
                            >
                                <div className="feature-icon" style={{ color: agent.color }}>
                                    <span className="agent-emoji">{agent.icon}</span>
                                </div>
                                <h3 className="feature-title">{agent.name}</h3>
                                <p className="feature-description">{agent.description}</p>
                                <div className="feature-capabilities">
                                    {agent.capabilities.slice(0, 3).map((capability, idx) => (
                                        <div key={idx} className="capability-item">✓ {capability}</div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="section cta">
                <div className="container">
                    <div className="cta-content">
                        <h2 className="cta-title">
                            Ready to Transform<br />Your Healthcare?
                        </h2>
                        <p className="cta-description">
                            Join thousands of patients and doctors experiencing the future of personalized medicine.
                        </p>
                        <div className="cta-buttons">
                            <Link to="/signup" className="btn btn-primary btn-large">
                                Get Started Free
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M7 3L14 10L7 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            </Link>
                            <Link to="/login" className="btn btn-outline btn-large">
                                Sign In
                            </Link>
                        </div>
                        <div className="mt-8 text-center">
                            <Link to="/doctor/dashboard" className="text-gray-500 hover:text-cyan-400 text-sm font-medium transition-colors flex items-center justify-center gap-2">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                                Access Doctor Portal
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}

export default LandingPage
