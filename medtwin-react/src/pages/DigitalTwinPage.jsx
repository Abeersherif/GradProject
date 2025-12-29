import { useState, useEffect, useRef } from 'react'
import './DigitalTwinPage.css'

const DigitalTwinPage = () => {
    const [userData, setUserData] = useState(null)
    const [simulationData, setSimulationData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedOrgan, setSelectedOrgan] = useState('all')
    const canvasRef = useRef(null)

    useEffect(() => {
        // Load user data
        const savedUserStr = localStorage.getItem('patientUser') || localStorage.getItem('user')
        if (savedUserStr) {
            try {
                setUserData(JSON.parse(savedUserStr))
            } catch (err) {
                console.error('Failed to parse user data:', err)
            }
        }
    }, [])

    // Initialize 3D scene with Three.js
    useEffect(() => {
        if (!canvasRef.current) return

        // Import Three.js dynamically
        import('three').then(THREE => {
            import('three/examples/jsm/loaders/GLTFLoader').then(({ GLTFLoader }) => {
                import('three/examples/jsm/controls/OrbitControls').then(({ OrbitControls }) => {
                    const canvas = canvasRef.current
                    const scene = new THREE.Scene()
                    scene.background = new THREE.Color(0x0a0a0a)

                    // Camera
                    const camera = new THREE.PerspectiveCamera(50, canvas.clientWidth / canvas.clientHeight, 0.1, 1000)
                    camera.position.set(0, 1.5, 4)

                    // Renderer
                    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
                    renderer.setSize(canvas.clientWidth, canvas.clientHeight)
                    renderer.setPixelRatio(window.devicePixelRatio)

                    // Lighting
                    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
                    scene.add(ambientLight)

                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
                    directionalLight.position.set(5, 5, 5)
                    scene.add(directionalLight)

                    const backLight = new THREE.DirectionalLight(0x6b46c1, 0.3)
                    backLight.position.set(-5, 3, -5)
                    scene.add(backLight)

                    // Controls
                    const controls = new OrbitControls(camera, canvas)
                    controls.enableDamping = true
                    controls.dampingFactor = 0.05
                    controls.minDistance = 2
                    controls.maxDistance = 10

                    // Create body representation
                    const bodyGroup = new THREE.Group()
                    const loader = new GLTFLoader()

                    // 1. Load Body/Skin (The Shell)
                    loader.load('/models/skin.glb', (gltf) => {
                        const model = gltf.scene
                        model.position.set(0, 0, 0)
                        model.scale.set(1, 1, 1)
                        model.traverse((child) => {
                            if (child.isMesh) {
                                child.material = new THREE.MeshPhongMaterial({
                                    color: 0xcccccc,
                                    transparent: true,
                                    opacity: 0.15,
                                    side: THREE.DoubleSide
                                })
                            }
                        })
                        bodyGroup.add(model)
                    }, undefined, (e) => {
                        // Fallback if model not found: create simple cylinder
                        const bodyGeometry = new THREE.CylinderGeometry(0.5, 0.4, 3, 32)
                        const bodyMaterial = new THREE.MeshPhongMaterial({ color: 0xf5f1e8, transparent: true, opacity: 0.1 })
                        bodyGroup.add(new THREE.Mesh(bodyGeometry, bodyMaterial))
                    })

                    // 2. Load Heart
                    loader.load('/models/heart.glb', (gltf) => {
                        const heart = gltf.scene
                        heart.position.set(0, 0, 0)
                        heart.scale.set(1, 1, 1)
                        heart.name = 'heart'
                        bodyGroup.add(heart)

                        // Add pulsing animation specifically to the heart scene
                        scene.userData.heartModel = heart
                    })

                    // 3. Load Pancreas
                    loader.load('/models/pancreas.glb', (gltf) => {
                        const pancreas = gltf.scene
                        pancreas.position.set(0, 0, 0)
                        pancreas.scale.set(1, 1, 1)
                        pancreas.name = 'pancreas'
                        bodyGroup.add(pancreas)
                    })

                    // 4. Load Kidneys
                    loader.load('/models/kidney_left.glb', (gltf) => {
                        const left = gltf.scene
                        left.position.set(0, 0, 0)
                        left.scale.set(1, 1, 1)
                        bodyGroup.add(left)
                    })
                    loader.load('/models/kidney_right.glb', (gltf) => {
                        const right = gltf.scene
                        right.position.set(0, 0, 0)
                        right.scale.set(1, 1, 1)
                        bodyGroup.add(right)
                    })

                    // 5. Load Vascular System
                    loader.load('/models/blood_vasculature.glb', (gltf) => {
                        const vessels = gltf.scene
                        vessels.position.set(0, 0, 0)
                        vessels.scale.set(1, 1, 1)
                        bodyGroup.add(vessels)
                    }, undefined, () => {
                        // Simple vessels fallback
                        const vascularMaterial = new THREE.LineBasicMaterial({ color: 0xa8b5a0, linewidth: 2 })
                        const points = [new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, -1, 0)]
                        const geometry = new THREE.BufferGeometry().setFromPoints(points)
                        bodyGroup.add(new THREE.Line(geometry, vascularMaterial))
                    })

                    scene.add(bodyGroup)

                    // Animation loop
                    let animationId
                    const animate = () => {
                        animationId = requestAnimationFrame(animate)

                        // Gentle rotation
                        bodyGroup.rotation.y += 0.002

                        // Pulse effect on heart (only if loaded)
                        const heartModel = scene.userData.heartModel
                        if (heartModel) {
                            const pulse = Math.sin(Date.now() * 0.003) * 0.03 + 1.0
                            heartModel.scale.set(pulse, pulse, pulse)
                        }

                        controls.update()
                        renderer.render(scene, camera)
                    }
                    animate()

                    // Handle resize
                    const handleResize = () => {
                        if (!canvas) return
                        camera.aspect = canvas.clientWidth / canvas.clientHeight
                        camera.updateProjectionMatrix()
                        renderer.setSize(canvas.clientWidth, canvas.clientHeight)
                    }
                    window.addEventListener('resize', handleResize)

                    // Cleanup
                    return () => {
                        window.removeEventListener('resize', handleResize)
                        if (animationId) cancelAnimationFrame(animationId)
                        renderer.dispose()
                    }
                })
            })
        }).catch(err => {
            console.error('Failed to load Three.js:', err)
        })
    }, [])

    const runSimulation = async () => {
        if (!userData || !userData.diseases) {
            alert('Please complete your health profile first!')
            return
        }

        setLoading(true)
        try {
            const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://medtwin.onrender.com';
            const BASE = VITE_API_URL.endsWith('/api') ? VITE_API_URL : `${VITE_API_URL}/api`;
            const response = await fetch(`${BASE}/twin/simulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    patient_id: userData.id,
                    conditions: userData.diseases,
                    age: userData.age,
                    glucose: userData.glucose || 100,
                    blood_pressure: userData.blood_pressure || '120/80'
                })
            })

            if (!response.ok) throw new Error('Simulation failed')

            const data = await response.json()
            setSimulationData(data)
        } catch (error) {
            console.error('Simulation error:', error)
            alert('Failed to run simulation. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    const organData = {
        heart: {
            name: 'Heart',
            color: '#e8b4b8',
            icon: '❤️',
            metrics: ['Heart Rate', 'Blood Pressure', 'Cardiac Output']
        },
        kidney: {
            name: 'Kidneys',
            color: '#6b46c1',
            icon: '🫘',
            metrics: ['Filtration Rate', 'Creatinine', 'Electrolytes']
        },
        pancreas: {
            name: 'Pancreas',
            color: '#d4af37',
            icon: '🥞',
            metrics: ['Insulin Production', 'Glucose Regulation', 'Enzyme Secretion']
        },
        vessels: {
            name: 'Vascular System',
            color: '#a8b5a0',
            icon: '🔴',
            metrics: ['Blood Flow', 'Oxygen Saturation', 'Vessel Health']
        }
    }

    const userInitials = (() => {
        if (!userData) return 'MT'
        if (userData.firstName && userData.lastName) {
            return `${userData.firstName[0]}${userData.lastName[0]}`.toUpperCase()
        }
        return 'MT'
    })()

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
                    <a href="/patient/dashboard" className="nav-item">
                        <span className="nav-icon">📊</span>
                        <span>Dashboard</span>
                    </a>
                    <a href="/patient/consultation" className="nav-item">
                        <span className="nav-icon">👨‍⚕️</span>
                        <span>Consultations</span>
                    </a>
                    <a href="/patient/medications" className="nav-item">
                        <span className="nav-icon">💊</span>
                        <span>Medications</span>
                    </a>
                    <a href="/patient/lab-results" className="nav-item">
                        <span className="nav-icon">🧪</span>
                        <span>Reports</span>
                    </a>
                    <a href="/patient/digital-twin" className="nav-item active">
                        <span className="nav-icon">🧬</span>
                        <span>3D Visualization</span>
                    </a>
                    <a href="/patient/profile" className="nav-item">
                        <span className="nav-icon">👤</span>
                        <span>Profile</span>
                    </a>
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
                        <h1>Digital Twin Visualization</h1>
                        <p>Interactive 3D model of your body systems with real-time health simulation</p>
                    </div>
                    <div className="header-actions">
                        <button
                            className="btn btn-primary"
                            onClick={runSimulation}
                            disabled={loading}
                        >
                            <span>🔬</span>
                            {loading ? 'Running...' : 'Run Simulation'}
                        </button>
                    </div>
                </header>

                <div className="twin-container">
                    {/* 3D Visualization */}
                    <section className="twin-3d-view">
                        <canvas ref={canvasRef} className="twin-canvas" />
                        <div className="twin-controls">
                            <button className="control-btn" title="Reset View">
                                <span>🔄</span>
                            </button>
                            <button className="control-btn" title="Zoom In">
                                <span>➕</span>
                            </button>
                            <button className="control-btn" title="Zoom Out">
                                <span>➖</span>
                            </button>
                        </div>
                    </section>

                    {/* Organ Selector */}
                    <aside className="twin-sidebar">
                        <h3 className="sidebar-title">Organ Systems</h3>
                        <div className="organ-list">
                            <button
                                className={`organ-btn ${selectedOrgan === 'all' ? 'active' : ''}`}
                                onClick={() => setSelectedOrgan('all')}
                            >
                                <span className="organ-icon">🫁</span>
                                <span>All Systems</span>
                            </button>
                            {Object.entries(organData).map(([key, organ]) => (
                                <button
                                    key={key}
                                    className={`organ-btn ${selectedOrgan === key ? 'active' : ''}`}
                                    onClick={() => setSelectedOrgan(key)}
                                    style={{ '--organ-color': organ.color }}
                                >
                                    <span className="organ-icon">{organ.icon}</span>
                                    <span>{organ.name}</span>
                                </button>
                            ))}
                        </div>

                        {selectedOrgan !== 'all' && organData[selectedOrgan] && (
                            <div className="organ-details">
                                <h4 style={{ color: organData[selectedOrgan].color }}>
                                    {organData[selectedOrgan].name} Metrics
                                </h4>
                                <ul className="metrics-list">
                                    {organData[selectedOrgan].metrics.map((metric, idx) => (
                                        <li key={idx}>{metric}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </aside>
                </div>

                {/* Simulation Results */}
                {simulationData && (
                    <section className="simulation-results">
                        <h2 className="section-title">Simulation Results</h2>
                        <div className="results-grid">
                            <div className="result-card">
                                <div className="result-header">
                                    <span className="result-icon">📊</span>
                                    <h3>Overall Health Score</h3>
                                </div>
                                <div className="result-value">
                                    {simulationData.health_score || 'N/A'}/100
                                </div>
                                <div className="result-status">
                                    {simulationData.overall_status || 'Calculating...'}
                                </div>
                            </div>

                            <div className="result-card">
                                <div className="result-header">
                                    <span className="result-icon">⚠️</span>
                                    <h3>Risk Factors</h3>
                                </div>
                                <ul className="risk-list">
                                    {simulationData.risk_factors?.map((risk, idx) => (
                                        <li key={idx}>{risk}</li>
                                    )) || <li>No significant risks detected</li>}
                                </ul>
                            </div>

                            <div className="result-card">
                                <div className="result-header">
                                    <span className="result-icon">💡</span>
                                    <h3>Recommendations</h3>
                                </div>
                                <ul className="recommendation-list">
                                    {simulationData.recommendations?.map((rec, idx) => (
                                        <li key={idx}>{rec}</li>
                                    )) || <li>Continue current treatment plan</li>}
                                </ul>
                            </div>
                        </div>
                    </section>
                )}

                {/* Info Panel */}
                <section className="info-panel">
                    <h3>About Digital Twin</h3>
                    <p>
                        Your digital twin is a personalized 3D model that simulates how your body systems interact based on your health data.
                        The simulation uses advanced AI algorithms to predict potential health outcomes and provide personalized recommendations.
                    </p>
                    <div className="info-features">
                        <div className="feature-item">
                            <span>🔬</span>
                            <span>Real-time simulation</span>
                        </div>
                        <div className="feature-item">
                            <span>📈</span>
                            <span>Predictive analytics</span>
                        </div>
                        <div className="feature-item">
                            <span>🎯</span>
                            <span>Personalized insights</span>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    )
}

export default DigitalTwinPage
