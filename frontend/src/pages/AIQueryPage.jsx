import { useState, useEffect, useRef } from 'react'
import { LocalMunicipalitySelector } from '../components/selectors/LocalMunicipalitySelector'
import { api } from '../api/client'

const YEARS = Array.from({ length: 26 }, (_, i) => 2024 - i)

export function AIQueryPage() {
  const [muni, setMuni] = useState(null)
  const [year, setYear] = useState(2024)
  const [compMunis, setCompMunis] = useState([])   // רשויות להשוואה
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [insights, setInsights] = useState([])
  const [insightsLoading, setInsightsLoading] = useState(false)
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    if (!muni) return
    setInsights([])
    setInsightsLoading(true)
    api.getInsights(muni.id, year)
      .then(r => setInsights(r.insights || []))
      .catch(() => setInsights([]))
      .finally(() => setInsightsLoading(false))
  }, [muni, year])

  const addCompMuni = () => {
    if (compMunis.length < 2) setCompMunis([...compMunis, null])
  }

  const updateCompMuni = (index, value) => {
    const updated = [...compMunis]
    updated[index] = value
    setCompMunis(updated)
  }

  const removeCompMuni = (index) => {
    setCompMunis(compMunis.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!muni || !question.trim()) return
    setLoading(true)
    setResult(null)
    const compIds = compMunis.filter(Boolean).map(m => m.id)
    try {
      const r = await api.aiQuery(question, muni.id, year, sessionId.current, compIds.length ? compIds : null)
      setResult(r)
    } catch (err) {
      const msg = err?.detail || err?.message || 'שגיאה בשרת. נסה שוב.'
      setResult({ answer: msg, sources: [], isError: true })
    } finally {
      setLoading(false)
    }
  }

  const isComparing = compMunis.some(Boolean)

  return (
    <div className="p-6 max-w-3xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">שאל על רשות מקומית</h1>

      {/* בחירת רשויות */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="flex gap-4 flex-wrap items-end">
          <div className="flex-1 min-w-48">
            <label className="text-sm text-gray-500 block mb-1">רשות ראשית</label>
            <LocalMunicipalitySelector value={muni} onChange={v => { setMuni(v); setResult(null) }} />
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">שנה</label>
            <select
              value={year}
              onChange={e => setYear(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm shadow-sm outline-none cursor-pointer"
              dir="rtl"
            >
              {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        {/* רשויות השוואה */}
        {compMunis.map((cm, i) => (
          <div key={i} className="flex gap-2 items-end mt-3">
            <div className="flex-1 min-w-48">
              <label className="text-sm text-gray-500 block mb-1">השוואה {i + 1}</label>
              <LocalMunicipalitySelector
                value={cm}
                onChange={v => updateCompMuni(i, v)}
                placeholder="חפש רשות להשוואה..."
              />
            </div>
            <button
              onClick={() => removeCompMuni(i)}
              className="mb-0.5 text-gray-400 hover:text-red-500 text-xl leading-none px-1"
              title="הסר"
            >×</button>
          </div>
        ))}

        {/* כפתור הוספה */}
        {muni && compMunis.length < 2 && (
          <button
            onClick={addCompMuni}
            className="mt-3 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span className="text-lg leading-none">+</span> הוסף רשות להשוואה
          </button>
        )}

        {isComparing && (
          <p className="mt-2 text-xs text-gray-400">
            השאלה תענה על בסיס השוואה בין {1 + compMunis.filter(Boolean).length} רשויות
          </p>
        )}
      </div>

      {/* תובנות אוטומטיות */}
      {insightsLoading && <div className="text-sm text-gray-400 mb-4">טוען תובנות...</div>}
      {insights.length > 0 && !isComparing && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <h3 className="font-semibold text-blue-800 mb-2 text-sm">תובנות אוטומטיות</h3>
          <ul className="space-y-1">
            {insights.map((ins, i) => (
              <li key={i} className="text-sm text-blue-900">• {ins}</li>
            ))}
          </ul>
        </div>
      )}

      {/* שאלה */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-4 mb-6">
        <label className="text-sm text-gray-500 block mb-2">שאל שאלה חופשית</label>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder={isComparing ? 'לדוגמה: איזו רשות מובילה בבגרות?' : 'לדוגמה: מה שיעור הבגרות לעומת הממוצע הארצי?'}
            className="flex-1 border rounded-lg px-3 py-2 text-sm"
            disabled={!muni}
          />
          <button
            type="submit"
            disabled={loading || !muni || !question.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-40"
          >
            {loading ? 'שולח...' : 'שלח'}
          </button>
        </div>
      </form>

      {/* תשובה */}
      {result && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className={`leading-relaxed mb-4 whitespace-pre-wrap ${result.isError ? 'text-red-600' : 'text-gray-900'}`}>
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
                    <span className="font-medium text-gray-700">{s.name_he}</span>:{' '}
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
