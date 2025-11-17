import { useState, useEffect } from 'react'
import { sendMessage, healthCheck } from './utils/api'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [loading, setLoading] = useState(false)
  const [healthy, setHealthy] = useState(false)

  useEffect(() => {
    // Generate session ID on mount
    setSessionId(crypto.randomUUID())

    // Check backend health
    healthCheck().then(setHealthy)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    try {
      const result = await sendMessage(question, sessionId)
      setResponse(result.response)
      setSessionId(result.session_id)
    } catch (error) {
      setResponse(error instanceof Error ? error.message : 'Villa kom upp')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Efnafræði Kennsluaðstoð</h1>
        <div className="health-indicator">
          <span className={healthy ? 'status-ok' : 'status-error'}>
            {healthy ? '● Tengt' : '● Ótengdur'}
          </span>
        </div>
      </header>

      <main>
        <form onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Skrifaðu spurninguna þína um efnafræði hér..."
            rows={4}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !healthy}>
            {loading ? 'Vinnsla...' : 'Senda spurningu'}
          </button>
        </form>

        {response && (
          <div className="response-box">
            <h2>Svar:</h2>
            <p>{response}</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
