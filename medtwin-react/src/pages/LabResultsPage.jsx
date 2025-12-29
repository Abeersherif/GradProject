import React, { useState } from 'react'
import { agentService } from '../services/api'
import Navbar from '../components/Navbar'
import './LabResultsPage.css'

// Helper function to format interpretation text with basic markdown
const formatInterpretation = (text) => {
    if (!text) return null

    // First, process bold text globally
    const processBold = (str) => {
        const parts = []
        let lastIndex = 0
        const boldRegex = /\*\*(.+?)\*\*/g
        let match

        while ((match = boldRegex.exec(str)) !== null) {
            // Add text before bold
            if (match.index > lastIndex) {
                parts.push(str.slice(lastIndex, match.index))
            }
            // Add bold text as JSX
            parts.push({ type: 'bold', text: match[1], key: match.index })
            lastIndex = match.index + match[0].length
        }

        // Add remaining text
        if (lastIndex < str.length) {
            parts.push(str.slice(lastIndex))
        }

        return parts.length > 0 ? parts : [str]
    }

    // Convert processed parts to JSX
    const renderParts = (parts, baseKey = 0) => {
        return parts.map((part, idx) => {
            if (typeof part === 'string') {
                return part
            } else if (part.type === 'bold') {
                return <strong key={`bold-${baseKey}-${idx}`}>{part.text}</strong>
            }
            return part
        })
    }

    // Split by paragraphs and numbered items
    const lines = text.split('\n')
    const elements = []
    let currentParagraph = []

    lines.forEach((line, lineIndex) => {
        // Check for numbered list item (e.g., "1. **Title:** content")
        const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/)

        if (numberedMatch) {
            // Flush current paragraph
            if (currentParagraph.length > 0) {
                const paraText = currentParagraph.join(' ')
                const parts = processBold(paraText)
                elements.push(<p key={`para-${lineIndex}`}>{renderParts(parts, lineIndex)}</p>)
                currentParagraph = []
            }

            const [, number, content] = numberedMatch
            const contentParts = processBold(content)

            // Check if content starts with bold title
            const titleMatch = content.match(/^\*\*(.+?)\*\*:?\s*(.*)$/)
            if (titleMatch) {
                elements.push(
                    <div key={`item-${lineIndex}`} className="interpretation-item">
                        <div className="item-number">{number}</div>
                        <div className="item-content">
                            <h4>{titleMatch[1]}</h4>
                            <p>{renderParts(processBold(titleMatch[2]), lineIndex)}</p>
                        </div>
                    </div>
                )
            } else {
                elements.push(
                    <div key={`item-${lineIndex}`} className="interpretation-item">
                        <div className="item-number">{number}</div>
                        <div className="item-content">
                            <p>{renderParts(contentParts, lineIndex)}</p>
                        </div>
                    </div>
                )
            }
        } else if (line.trim() === '') {
            // Empty line - flush paragraph
            if (currentParagraph.length > 0) {
                const paraText = currentParagraph.join(' ')
                const parts = processBold(paraText)
                elements.push(<p key={`para-${lineIndex}`}>{renderParts(parts, lineIndex)}</p>)
                currentParagraph = []
            }
        } else {
            // Regular line - add to current paragraph
            currentParagraph.push(line)
        }
    })

    // Flush remaining paragraph
    if (currentParagraph.length > 0) {
        const paraText = currentParagraph.join(' ')
        const parts = processBold(paraText)
        elements.push(<p key="para-final">{renderParts(parts, 'final')}</p>)
    }

    return elements
}

const LabResultsPage = () => {
    const [selectedFile, setSelectedFile] = useState(null)
    const [interpretation, setInterpretation] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [dragActive, setDragActive] = useState(false)

    const handleFileSelect = (e) => {
        const file = e.target.files[0]
        if (file) {
            // Validate file type (PDF, image, or text)
            const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'text/plain']
            if (validTypes.includes(file.type)) {
                setSelectedFile(file)
                setError('')
            } else {
                setError('Please upload a PDF, image (JPG/PNG), or text file')
                setSelectedFile(null)
            }
        }
    }

    const handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0]
            const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'text/plain']
            if (validTypes.includes(file.type)) {
                setSelectedFile(file)
                setError('')
            } else {
                setError('Please upload a PDF, image (JPG/PNG), or text file')
            }
        }
    }

    const handleUpload = async () => {
        if (!selectedFile) {
            setError('Please select a file first')
            return
        }

        setLoading(true)
        setError('')

        try {
            const result = await agentService.interpretLabResults(selectedFile)
            setInterpretation(result)
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to interpret lab results. Please try again.')
            console.error('Lab results error:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleReset = () => {
        setSelectedFile(null)
        setInterpretation(null)
        setError('')
    }

    return (
        <div className="lab-results-page">
            <Navbar />

            <div className="lab-results-container">
                <header className="lab-header">
                    <div className="lab-header-content">
                        <div className="lab-icon">🧪</div>
                        <div>
                            <h1>Lab Results Interpretation</h1>
                            <p>Upload your lab reports for AI-powered analysis and insights</p>
                        </div>
                    </div>
                </header>

                <div className="lab-content">
                    {!interpretation ? (
                        <div className="upload-section">
                            <div
                                className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                            >
                                <input
                                    type="file"
                                    id="lab-file-input"
                                    onChange={handleFileSelect}
                                    accept=".pdf,.jpg,.jpeg,.png,.txt"
                                    style={{ display: 'none' }}
                                />

                                {!selectedFile ? (
                                    <label htmlFor="lab-file-input" className="upload-prompt">
                                        <div className="upload-icon">📄</div>
                                        <h3>Drop your lab results here</h3>
                                        <p>or click to browse files</p>
                                        <span className="file-types">Supported: PDF, JPG, PNG, TXT</span>
                                    </label>
                                ) : (
                                    <div className="file-selected">
                                        <div className="file-icon">✓</div>
                                        <div className="file-info">
                                            <h4>{selectedFile.name}</h4>
                                            <p>{(selectedFile.size / 1024).toFixed(2)} KB</p>
                                        </div>
                                        <button onClick={handleReset} className="btn-reset">✕</button>
                                    </div>
                                )}
                            </div>

                            {error && (
                                <div className="error-message">
                                    <span>⚠️</span>
                                    {error}
                                </div>
                            )}

                            {selectedFile && (
                                <button
                                    onClick={handleUpload}
                                    disabled={loading}
                                    className="btn btn-primary btn-upload"
                                >
                                    {loading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            🔍 Analyze Lab Results
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                    ) : (
                        <div className="interpretation-section">
                            <div className="interpretation-header">
                                <h2>📊 Analysis Complete</h2>
                                <button onClick={handleReset} className="btn btn-outline">
                                    Upload New Results
                                </button>
                            </div>

                            <div className="interpretation-content">
                                {interpretation.interpretation && (
                                    <div className="interpretation-block">
                                        <h3>🔬 Medical Interpretation</h3>
                                        <div className="interpretation-text formatted">
                                            {formatInterpretation(interpretation.interpretation)}
                                        </div>
                                    </div>
                                )}

                                {interpretation.abnormal_values && interpretation.abnormal_values.length > 0 && (
                                    <div className="interpretation-block alert-block">
                                        <h3>⚠️ Abnormal Values Detected</h3>
                                        <ul className="abnormal-list">
                                            {interpretation.abnormal_values.map((item, index) => (
                                                <li key={index}>
                                                    <strong>{item.test}:</strong> {item.value} {item.unit}
                                                    {item.reference && <span className="reference"> (Normal: {item.reference})</span>}
                                                    {item.significance && <p className="significance">{item.significance}</p>}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {interpretation.recommendations && (
                                    <div className="interpretation-block">
                                        <h3>💡 Recommendations</h3>
                                        <div className="interpretation-text formatted">
                                            {formatInterpretation(interpretation.recommendations)}
                                        </div>
                                    </div>
                                )}

                                {interpretation.follow_up_required && (
                                    <div className="interpretation-block warning-block">
                                        <h3>🚨 Follow-Up Required</h3>
                                        <p>{interpretation.follow_up_message || 'Please consult with your healthcare provider regarding these results.'}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                <div className="lab-footer">
                    <p className="disclaimer">
                        ⚕️ This AI interpretation is for informational purposes only and should not replace professional medical advice. Always consult with your healthcare provider about your lab results.
                    </p>
                </div>
            </div>
        </div>
    )
}

export default LabResultsPage
