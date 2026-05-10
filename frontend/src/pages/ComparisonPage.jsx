import { useState, useEffect } from 'react'
import { LocalMunicipalitySelector } from '../components/selectors/LocalMunicipalitySelector'
import { CompareChart } from '../components/charts/CompareChart'
import { api } from '../api/client'

const MAX_MUNIS = 6
const years = Array.from({ length: 26 }, (_, i) => 2024 - i)

export function ComparisonPage() {
  const [munis, setMunis] = useState([null, null])
  const [indicatorCode, setIndicatorCode] = useState('')
  const [indicatorsByDomain, setIndicatorsByDomain] = useState({})
  const yearFrom = 1999
  const yearTo = 2024
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getIndicators().then(setIndicatorsByDomain).catch(() => {})
  }, [])

  const setMuni = (idx, val) => setMunis(prev => prev.map((m, i) => i === idx ? val : m))

  const addMuni = () => {
    if (munis.length < MAX_MUNIS) setMunis(prev => [...prev, null])
  }

  const removeMuni = (idx) => {
    if (munis.length <= 2) return
    setMunis(prev => prev.filter((_, i) => i !== idx))
    setData(null)
  }

  const selectedMunis = munis.filter(Boolean)
  const canCompare = selectedMunis.length >= 2 && indicatorCode

  const handleCompare = async () => {
    if (!canCompare) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const result = await api.compare(selectedMunis.map(m => m.id), indicatorCode, yearFrom, yearTo)
      setData(result)
    } catch {
      setError('שגיאה בטעינת הנתונים. נסה שנית.')
    } finally {
      setLoading(false)
    }
  }

  const ordinals = ['ראשונה', 'שנייה', 'שלישית', 'רביעית', 'חמישית', 'שישית']

  return (
    <div className="p-6 max-w-6xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">השוואת רשויות</h1>

      <div className="bg-white rounded-xl shadow p-4 mb-6">

        {/* Municipality selectors */}
        <div className="flex flex-wrap gap-3 mb-4">
          {munis.map((muni, idx) => (
            <div key={idx} className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-500">רשות {ordinals[idx]}</label>
                {munis.length > 2 && (
                  <button onClick={() => removeMuni(idx)}
                          className="text-gray-300 hover:text-red-400 text-lg leading-none mr-2">×</button>
                )}
              </div>
              <LocalMunicipalitySelector
                value={muni}
                onChange={val => setMuni(idx, val)}
                placeholder={`חפש רשות...`}
              />
            </div>
          ))}

          {munis.length < MAX_MUNIS && (
            <div className="flex flex-col justify-end">
              <button onClick={addMuni}
                      className="border-2 border-dashed border-gray-300 rounded-lg px-4 py-2 text-sm text-gray-400 hover:border-blue-400 hover:text-blue-500 transition whitespace-nowrap">
                + הוסף רשות
              </button>
            </div>
          )}
        </div>

        {/* Indicator + years + button */}
        <div className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="text-sm text-gray-500 block mb-1">מדד</label>
            <select value={indicatorCode} onChange={e => setIndicatorCode(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm min-w-52" dir="rtl">
              <option value="">בחר מדד</option>
              {Object.entries(indicatorsByDomain).map(([domain, indicators]) => (
                <optgroup key={domain} label={domain}>
                  {indicators.map(ind => (
                    <option key={ind.code} value={ind.code}>{ind.name_he}</option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <button onClick={handleCompare} disabled={!canCompare || loading}
                  className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
                    canCompare && !loading
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}>
            {loading ? 'טוען...' : `השווה (${selectedMunis.length} רשויות)`}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">{error}</div>
      )}

      {loading && (
        <div className="text-center text-gray-400 py-16 text-sm">טוען נתוני השוואה...</div>
      )}

      {data && !loading && <CompareChart data={data} />}

      {!data && !loading && !error && (
        <div className="text-center text-gray-400 py-16 text-sm">
          בחר לפחות שתי רשויות ומדד כדי להתחיל השוואה
        </div>
      )}
    </div>
  )
}
