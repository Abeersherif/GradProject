import { useState, useEffect, useRef } from 'react'
import './DigitalTwinPage.css'

const DigitalTwinPage = () => {
    const [userData, setUserData] = useState(null)
    const [simulationData, setSimulationData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedOrgan, setSelectedOrgan] = useState('all')
    const [timelineYear, setTimelineYear] = useState(2025)
    const canvasRef = useRef(null)
    const sceneRef = useRef(null)

    useEffect(() => {
        const savedUserStr = localStorage.getItem('patientUser') || localStorage.getItem('user')
        if (savedUserStr) {
            try {
                const parsed = JSON.parse(savedUserStr)
                setUserData(parsed)
                // Trigger initial simulation for current year
                runSimulation(parsed.id, 0)
            } catch (err) {
                console.error('Failed to parse user data:', err)
            }
        }
    }, [])

    const runSimulation = async (patientId, yearsAhead = 0) => {
        setLoading(true)
        try {
            const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://medtwin.onrender.com';
            const BASE = VITE_API_URL.endsWith('/api') ? VITE_API_URL : `${VITE_API_URL}/api`;

            // Call the correct visualization-data endpoint
            const response = await fetch(`${BASE}/twin/${patientId}/visualization-data?years_ahead=${yearsAhead}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })

            if (!response.ok) throw new Error('Simulation failed')

            const data = await response.json()
            setSimulationData(data)

            // Update 3D model colors based on organ status
            updateModelColors(data.organs)
        } catch (error) {
            console.error('Simulation error:', error)
        } finally {
            setLoading(false)
        }
    }

    const updateModelColors = (organs) => {
        if (!sceneRef.current || !organs) return

        sceneRef.current.traverse((child) => {
            if (child.isMesh && child.name) {
                const name = child.name.toLowerCase()
                let color = null

                if (name.includes('heart')) color = organs.heart?.color
                if (name.includes('pancreas')) color = organs.pancreas?.color
                if (name.includes('kidney')) color = organs.kidneys?.color
                if (name.includes('vessel') || name.includes('blood')) color = organs.vessels?.color

                if (color) {
                    const mappedColor = color === 'red' ? 0xff4d4d : color === 'yellow' ? 0xffcc00 : 0x00ff88
                    child.material.color.setHex(mappedColor)
                    child.material.emissive = new (sceneRef.current.constructor).Color(mappedColor)
                    child.material.emissiveIntensity = 0.2
                }
            }
        })
    }

    const handleYearChange = (e) => {
        const year = parseInt(e.target.value)
        setTimelineYear(year)
        if (userData?.id) {
            runSimulation(userData.id, year - 2025)
        }
    }

    // Initialize 3D scene
    useEffect(() => {
        if (!canvasRef.current) return

        import('three').then(THREE => {
            import('three/examples/jsm/loaders/GLTFLoader').then(({ GLTFLoader }) => {
                import('three/examples/jsm/controls/OrbitControls').then(({ OrbitControls }) => {
                    const canvas = canvasRef.current
                    const scene = new THREE.Scene()
                    sceneRef.current = scene
                    scene.background = new THREE.Color(0x0a0a0d)

                    const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000)
                    camera.position.set(0, 1.2, 3.5)

                    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })
                    renderer.setSize(canvas.clientWidth, canvas.clientHeight)
                    renderer.setPixelRatio(window.devicePixelRatio)

                    // Better lighting for medical aesthetic
                    scene.add(new THREE.AmbientLight(0xffffff, 0.4))

                    const frontLight = new THREE.PointLight(0xffffff, 0.8)
                    frontLight.position.set(0, 2, 4)
                    scene.add(frontLight)

                    const rimLight = new THREE.DirectionalLight(0x4080ff, 0.5)
                    rimLight.position.set(-2, 2, -2)
                    scene.add(rimLight)

                    const controls = new OrbitControls(camera, canvas)
                    controls.enableDamping = true
                    controls.dampingFactor = 0.05
                    controls.minDistance = 1.5
                    controls.maxDistance = 6
                    controls.target.set(0, 1, 0)

                    const bodyGroup = new THREE.Group()
                    const loader = new GLTFLoader()

                    // Handle gender models
                    const isFemale = userData?.gender?.toLowerCase() === 'female' || userData?.sex?.toLowerCase() === 'female'
                    const suffix = isFemale ? '_female' : ''

                    // 1. Load Body
                    loader.load(`/models/skin${suffix}.glb`, (gltf) => {
                        const model = gltf.scene
                        model.traverse((child) => {
                            if (child.isMesh) {
                                child.material = new THREE.MeshPhongMaterial({
                                    color: 0x1a2a4a,
                                    transparent: true,
                                    opacity: 0.15,
                                    side: THREE.DoubleSide
                                })
                            }
                        })
                        bodyGroup.add(model)
                    }, undefined, () => {
                        const geo = new THREE.CylinderGeometry(0.5, 0.4, 2.5, 32)
                        bodyGroup.add(new THREE.Mesh(geo, new THREE.MeshPhongMaterial({ color: 0x112233, transparent: true, opacity: 0.2 })))
                    })

                    // 2. Load Internal Organs
                    const organs = [
                        { name: 'heart', file: `heart${suffix}.glb` },
                        { name: 'pancreas', file: `pancreas${suffix}.glb` },
                        { name: 'kidney_left', file: `kidney_left${suffix}.glb` },
                        { name: 'kidney_right', file: `kidney_right${suffix}.glb` },
                        { name: 'eye_left', file: `eye_left${suffix}.glb` },
                        { name: 'eye_right', file: `eye_right${suffix}.glb` },
                        { name: 'vasculature', file: `blood_vasculature.glb` }
                    ]

                    organs.forEach(org => {
                        loader.load(`/models/${org.file}`, (gltf) => {
                            const model = gltf.scene
                            model.name = org.name
                            model.traverse(child => {
                                if (child.isMesh) {
                                    child.material = new THREE.MeshPhongMaterial({
                                        color: 0x444444,
                                        shininess: 50
                                    })
                                }
                            })
                            bodyGroup.add(model)
                            if (org.name === 'heart') scene.userData.heartModel = model
                        })
                    })

                    scene.add(bodyGroup)

                    let animationId
                    const animate = () => {
                        animationId = requestAnimationFrame(animate)
                        bodyGroup.rotation.y += 0.001

                        if (scene.userData.heartModel) {
                            const scale = 1.0 + Math.sin(Date.now() * 0.002) * 0.01 // Very subtle pulse
                            scene.userData.heartModel.scale.set(scale, scale, scale)
                        }

                        controls.update()
                        renderer.render(scene, camera)
                    }
                    animate()

                    const handleResize = () => {
                        camera.aspect = canvas.clientWidth / canvas.clientHeight
                        camera.updateProjectionMatrix()
                        renderer.setSize(canvas.clientWidth, canvas.clientHeight)
                    }
                    window.addEventListener('resize', handleResize)

                    return () => {
                        window.removeEventListener('resize', handleResize)
                        cancelAnimationFrame(animationId)
                        renderer.dispose()
                    }
                })
            })
        })
    }, [userData])

    const fullName = userData?.firstName && userData?.lastName
        ? `${userData.firstName} ${userData.lastName}`
        : (userData?.fullName || userData?.full_name || 'Guest User')

    return (
        <div className="twin-page-v2">
            {/* Sidebar (Main App) remains, but we wrap our layout inside dashboard-main */}
            <div className="visual-interface">

                {/* Top Title Overlay */}
                <div className="title-overlay">
                    <h2>PREDICTIVE ORGAN ANALYSIS</h2>
                    <div className="glow-bar"></div>
                </div>

                <div className="interface-grid">
                    {/* LEFT PANEL: BIOMETRICS & AI */}
                    <aside className="left-panel">
                        <section className="subject-card glass-card">
                            <div className="subject-header">
                                <div className="subject-id">
                                    <span className="label">Subject 001</span>
                                    <span className="id-val">{userData?.id?.substring(0, 8) || 'DM_00000'}</span>
                                </div>
                                <div className="status-dot online"></div>
                            </div>
                            <button className="load-btn">LOAD</button>
                        </section>

                        <section className="biometrics-grid">
                            <div className="bio-card glass-card">
                                <span className="bio-label">AGE</span>
                                <span className="bio-value">{userData?.age || 58}</span>
                            </div>
                            <div className="bio-card glass-card">
                                <span className="bio-label">SEX</span>
                                <span className="bio-value">{userData?.gender || userData?.sex || 'Female'}</span>
                            </div>
                            <div className="bio-card glass-card warning">
                                <span className="bio-label">HBA1C</span>
                                <span className="bio-value">{userData?.hba1c || '10.9'}%</span>
                                <div className="indicator-line orange"></div>
                            </div>
                            <div className="bio-card glass-card">
                                <span className="bio-label">BMI</span>
                                <span className="bio-value">{userData?.bmi || '35.8'}</span>
                            </div>
                        </section>

                        <section className="risk-legend glass-card">
                            <h4>RISK LEGEND</h4>
                            <div className="legend-item">
                                <span className="dot low"></span>
                                <span>Low Risk - Healthy</span>
                            </div>
                            <div className="legend-item">
                                <span className="dot moderate"></span>
                                <span>Moderate Risk</span>
                            </div>
                            <div className="legend-item">
                                <span className="dot high"></span>
                                <span>High Risk - Critical</span>
                            </div>
                        </section>

                        <section className="ai-report-card glass-card">
                            <h4>COGNITIVE BRAIN ANALYSIS</h4>
                            <div className="ai-btn-wrapper">
                                <div className="ai-btn-content">
                                    <span className="brain-icon">🧠</span>
                                    <div className="ai-text">
                                        <p className="main">View AI Analysis</p>
                                        <p className="sub">Cognitive System {simulationData ? 'Online' : 'Offline'}...</p>
                                    </div>
                                    <span className="arrow">→</span>
                                </div>
                            </div>
                        </section>
                    </aside>

                    {/* CENTER PANEL: 3D VIEW */}
                    <section className="center-view">
                        <canvas ref={canvasRef} className="twin-canvas-v2" />
                    </section>

                    {/* RIGHT PANEL: ORGAN STATUS */}
                    <aside className="right-panel">
                        <div className="organs-list-card glass-card">
                            <h3>Organ Systems</h3>
                            <p className="sub-hint">Click organ to focus</p>

                            <div className="organ-status-rows">
                                <div className="status-row">
                                    <span className="org-name">PANCREAS</span>
                                    <span className={`status-tag ${simulationData?.organs?.pancreas?.risk_level || 'moderate'}`}>
                                        {simulationData?.organs?.pancreas?.risk_level || 'moderate'}
                                    </span>
                                </div>
                                <div className="status-row">
                                    <span className="org-name">VESSELS</span>
                                    <span className={`status-tag ${simulationData?.organs?.vessels?.risk_level || 'low'}`}>
                                        {simulationData?.organs?.vessels?.risk_level || 'low'}
                                    </span>
                                </div>
                                <div className="status-row">
                                    <span className="org-name">KIDNEYS</span>
                                    <span className={`status-tag ${simulationData?.organs?.kidneys?.risk_level || 'high'}`}>
                                        {simulationData?.organs?.kidneys?.risk_level || 'high'}
                                    </span>
                                </div>
                                <div className="status-row">
                                    <span className="org-name">EYES</span>
                                    <span className={`status-tag ${simulationData?.organs?.eyes?.risk_level || 'high'}`}>
                                        {simulationData?.organs?.eyes?.risk_level || 'high'}
                                    </span>
                                </div>
                                <div className="status-row">
                                    <span className="org-name">HEART</span>
                                    <span className={`status-tag ${simulationData?.organs?.heart?.risk_level || 'high'}`}>
                                        {simulationData?.organs?.heart?.risk_level || 'high'}
                                    </span>
                                </div>
                            </div>

                            <div className="view-controls-hint">
                                <p><span>🖱️</span> ROTATE: Drag</p>
                                <p><span>🔍</span> ZOOM: Scroll</p>
                                <p><span>🎯</span> FOCUS: Click organ</p>
                            </div>
                        </div>
                    </aside>
                </div>

                {/* BOTTOM PANEL: TIMELINE SLIDER */}
                <footer className="timeline-footer">
                    <div className="slider-container glass-card">
                        <span className="slider-label">FUTURE PREDICTION</span>
                        <input
                            type="range"
                            min="2025"
                            max="2035"
                            step="1"
                            value={timelineYear}
                            onChange={handleYearChange}
                            className="year-slider"
                        />
                        <span className="year-display">{timelineYear}</span>
                    </div>
                </footer>

            </div>
        </div>
    )
}

export default DigitalTwinPage
