import { useState, useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import './DigitalTwinPage.css'

const DigitalTwinPage = () => {
    const [userData, setUserData] = useState(null)
    const [simulationData, setSimulationData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [timelineYear, setTimelineYear] = useState(2025)
    const canvasRef = useRef(null)
    const rendererRef = useRef(null)
    const sceneRef = useRef(null)
    const bodyGroupRef = useRef(new THREE.Group())
    const heartModelRef = useRef(null)

    useEffect(() => {
        const savedUserStr = localStorage.getItem('patientUser') || localStorage.getItem('user')
        if (savedUserStr) {
            try {
                const parsed = JSON.parse(savedUserStr)
                setUserData(parsed)
                if (parsed?.id) {
                    runSimulation(parsed.id, 0)
                }
            } catch (err) {
                console.error('Failed to parse user data:', err)
            }
        }
    }, [])

    const runSimulation = async (patientId, yearsAhead = 0) => {
        const id = patientId || 1;
        setLoading(true)
        try {
            const VITE_API_URL = import.meta.env.VITE_API_URL || 'https://medtwin-backend.onrender.com';
            const BASE = VITE_API_URL.endsWith('/api') ? VITE_API_URL : `${VITE_API_URL}/api`;
            const token = localStorage.getItem('patientToken') || localStorage.getItem('authToken');

            const response = await fetch(`${BASE}/twin/${id}/visualization-data?years_ahead=${yearsAhead}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Simulation failed');
            }

            const data = await response.json()
            setSimulationData(data)
            updateModelColors(data.organs)
        } catch (error) {
            console.error('Simulation error:', error)
        } finally {
            setLoading(false)
        }
    }

    const updateModelColors = (organs) => {
        if (!bodyGroupRef.current || !organs) return

        bodyGroupRef.current.traverse((child) => {
            if (child.isMesh) {
                const name = (child.name || child.parent?.name || '').toLowerCase()
                let color = null

                if (name.includes('heart')) color = organs.heart?.color
                else if (name.includes('pancreas')) color = organs.pancreas?.color
                else if (name.includes('kidney')) color = organs.kidneys?.color
                else if (name.includes('vessel') || name.includes('blood') || name.includes('vasculature')) color = organs.vessels?.color
                else if (name.includes('eye')) color = organs.eyes?.color

                if (color) {
                    const mappedColor = color === 'red' ? 0xff4d4d : color === 'yellow' ? 0xffcc00 : 0x00ff88
                    child.material.color.setHex(mappedColor)
                    if (child.material.emissive) {
                        child.material.emissive.setHex(mappedColor)
                        child.material.emissiveIntensity = 0.5
                    }
                }
            }
        })
    }

    const handleYearChange = (e) => {
        const year = parseInt(e.target.value)
        setTimelineYear(year)
        runSimulation(userData?.id || 1, year - 2025)
    }

    useEffect(() => {
        if (!canvasRef.current) return

        const canvas = canvasRef.current
        const scene = new THREE.Scene()
        sceneRef.current = scene
        scene.background = new THREE.Color(0x0a0a14)

        const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000)
        camera.position.set(0, 0, 10.5) // Move MUCH further back

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })
        renderer.setSize(canvas.clientWidth, canvas.clientHeight)
        renderer.setPixelRatio(window.devicePixelRatio)
        rendererRef.current = renderer

        scene.add(new THREE.AmbientLight(0xffffff, 1.0))

        const frontLight = new THREE.PointLight(0xffffff, 1.5)
        frontLight.position.set(0, 2, 4)
        scene.add(frontLight)

        const controls = new OrbitControls(camera, canvas)
        controls.enableDamping = true
        controls.dampingFactor = 0.05
        controls.minDistance = 1.0
        controls.maxDistance = 50
        controls.target.set(0, 0, 0)

        const bodyGroup = bodyGroupRef.current
        bodyGroup.scale.set(0.8, 0.8, 0.8) // Balanced scale



        scene.add(bodyGroup)

        const loader = new GLTFLoader()
        const isFemale = userData?.gender?.toLowerCase() === 'female' || userData?.sex?.toLowerCase() === 'female'
        const suffix = isFemale ? '_female' : ''

        // 1. Load Body
        loader.load(`/models/skin${suffix}.glb`, (gltf) => {
            const model = gltf.scene
            console.log('✅ Body model loaded successfully')
            model.traverse((child) => {
                if (child.isMesh) {
                    child.material = new THREE.MeshPhongMaterial({
                        color: 0x4a5a7a,
                        transparent: true,
                        opacity: 0.08, // Very faint body shell
                        side: THREE.DoubleSide
                    })
                }
            })
            bodyGroup.add(model)
        }, undefined, (error) => {
            console.error('❌ Failed to load body model:', error)
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
                console.log(`✅ Loaded ${org.name}`)

                // Assign realistic colors to organs
                let organColor = 0xcc8899 // Default pinkish
                if (org.name === 'heart') organColor = 0xcc4444
                if (org.name === 'pancreas') organColor = 0xddaa66
                if (org.name.includes('kidney')) organColor = 0x884444
                if (org.name.includes('eye')) organColor = 0xeeeeff
                if (org.name === 'vasculature') organColor = 0xff6666

                model.traverse(child => {
                    if (child.isMesh) {
                        child.material = new THREE.MeshPhongMaterial({
                            color: organColor,
                            shininess: 80,
                            specular: 0x222222
                        })
                        child.name = org.name // Preserve name for traversal
                    }
                })
                bodyGroup.add(model)
                if (org.name === 'heart') heartModelRef.current = model
            }, undefined, (error) => {
                console.error(`❌ Failed to load ${org.name}:`, error)
            })
        })

        let animationId
        const animate = () => {
            animationId = requestAnimationFrame(animate)
            bodyGroup.rotation.y += 0.001

            if (heartModelRef.current) {
                const scale = 1.0 + Math.sin(Date.now() * 0.002) * 0.02
                heartModelRef.current.scale.set(scale, scale, scale)
            }

            controls.update()
            renderer.render(scene, camera)
        }
        animate()

        const handleResize = () => {
            if (!canvasRef.current) return
            camera.aspect = canvas.clientWidth / canvas.clientHeight
            camera.updateProjectionMatrix()
            renderer.setSize(canvas.clientWidth, canvas.clientHeight)
        }
        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            cancelAnimationFrame(animationId)
            bodyGroup.clear() // Remove children
            rendererRef.current?.dispose()
        }
    }, [userData])

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
                                    <span className="id-val">{userData?.id ? String(userData.id).substring(0, 8) : 'DM_00000'}</span>
                                </div>
                                <div className="status-dot online"></div>
                            </div>
                            <button className="load-btn" onClick={() => runSimulation(userData?.id, 0)}>REFRESH</button>
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
                                        <p className="main">AI Simulation Ready</p>
                                        <p className="sub">{loading ? 'Processing...' : 'Cognitive System Active'}</p>
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
                            <p className="sub-hint">Real-time status analysis</p>

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
                                <p><span>🎯</span> PREDICTION: Use Slider</p>
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
