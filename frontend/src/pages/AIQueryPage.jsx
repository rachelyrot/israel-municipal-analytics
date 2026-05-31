import { useState, useRef } from 'react'
import { api } from '../api/client'

export function AIQueryPage() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const sessionId = useRef(crypto.randomUUID())

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const r = await api.aiQuery(question, null, null, sessionId.current, null)
      setResult(r)
    } catch (err) {
      const raw = err?.detail
      const msg = Array.isArray(raw)
        ? raw.map(e => e.msg || JSON.stringify(e)).join('; ')
        : (typeof raw === 'string' ? raw : err?.message) || 'שגיאה בשרת. נסה שוב.'
      setResult({ answer: msg, sources: [], isError: true })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-2">שאל AI</h1>
      <p className="text-sm text-gray-500 mb-6">
        שאל כל שאלה על רשויות מקומיות בישראל — לפי שנה, השוואה, מגמות ועוד
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="flex gap-2">
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="לדוגמה: אלו רשויות הובילו תעסוקה ב2024 לאומת 2022?"
            className="flex-1 border rounded-lg px-3 py-2 text-sm"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-40 whitespace-nowrap"
          >
            {loading ? 'שולח...' : 'שלח'}
          </button>
        </div>
      </form>

      {loading && (
        <div className="text-center text-gray-400 py-8 text-sm">מנתח נתונים...</div>
      )}

      {result && !loading && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className={`leading-relaxed whitespace-pre-wrap ${result.isError ? 'text-red-600' : 'text-gray-900'}`}>
            {result.answer}
          </p>
          {result.sources?.length > 0 && (
            <details className="mt-4">
              <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
                מקורות ({result.sources.length} נקודות נתונים)
              </summary>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {result.sources.slice(0, 20).map((s, i) => (
                  <div key={i} className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1">
                    {s.municipality && <span className="text-blue-600 font-medium">{s.municipality} · </span>}
                    <span className="font-medium text-gray-700">{s.name_he}</span>
                    {s.year && <span className="text-gray-400"> ({s.year})</span>}:{' '}
                    {s.value?.toLocaleString('he-IL')} {s.unit}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
