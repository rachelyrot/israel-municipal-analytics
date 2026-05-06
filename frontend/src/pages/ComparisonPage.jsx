import { useState, useEffect } from 'react'
import { LocalMunicipalitySelector } from '../components/selectors/LocalMunicipalitySelector'
import { CompareChart } from '../components/charts/CompareChart'
import { api } from '../api/client'

export function ComparisonPage() {
  const [muni1, setMuni1] = useState(null)
  const [muni2, setMuni2] = useState(null)
  const [indicatorCode, setIndicatorCode] = useState('')
  // getIndicators() returns { domain: [...indicators] } — store as-is
  const [indicatorsByDomain, setIndicatorsByDomain] = useState({})
  const [yearFrom, setYearFrom] = useState(2010)
  const [yearTo, setYearTo] = useState(2023)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const years = Array.from({ length: 26 }, (_, i) => 2024 - i)

  useEffect(() => {
    api.getIndicators()
      .then(setIndicatorsByDomain)
      .catch(() => {})
  }, [])

  const handleCompare = async () => {
    if (!muni1 || !muni2 || !indicatorCode) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const result = await api.compare([muni1.id, muni2.id], indicatorCode, yearFrom, yearTo)
      setData(result)
    } catch (e) {
      setError('שגיאה בטעינת הנתונים. נסה שנית.')
    } finally {
      setLoading(false)
    }
  }

  const canCompare = muni1 && muni2 && indicatorCode

  return (
    <div className="p-6 max-w-5xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">השוואת רשויות</h1>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow p-4 flex gap-4 flex-wrap items-end mb-6">
        {/* Municipality 1 */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">רשות ראשונה</label>
          <LocalMunicipalitySelector
            value={muni1}
            onChange={setMuni1}
            placeholder="חפש רשות ראשונה..."
          />
        </div>

        {/* Municipality 2 */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">רשות שנייה</label>
          <LocalMunicipalitySelector
            value={muni2}
            onChange={setMuni2}
            placeholder="חפש רשות שנייה..."
          />
        </div>

        {/* Indicator selector */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">מדד</label>
          <select
            value={indicatorCode}
            onChange={e => setIndicatorCode(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm min-w-48"
            dir="rtl"
          >
            <option value="">בחר מדד</option>
            {Object.entries(indicatorsByDomain).map(([domain, indicators]) => (
              <optgroup key={domain} label={domain}>
                {indicators.map(ind => (
                  <option key={ind.code} value={ind.code}>
                    {ind.name_he}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Year range */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">משנה</label>
          <select value={yearFrom} onChange={e => setYearFrom(Number(e.target.value))}
                  className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm" dir="rtl">
            {years.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm text-gray-500 block mb-1">עד שנה</label>
          <select value={yearTo} onChange={e => setYearTo(Number(e.target.value))}
                  className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm" dir="rtl">
            {years.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>

        {/* Compare button */}
        <button
          onClick={handleCompare}
          disabled={!canCompare || loading}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            canCompare && !loading
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {loading ? 'טוען...' : 'השווה'}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="text-center text-gray-400 py-16 text-sm">טוען נתוני השוואה...</div>
      )}

      {/* Chart */}
      {data && !loading && (
        <CompareChart data={data} />
      )}

      {/* Empty state */}
      {!data && !loading && !error && (
        <div className="text-center text-gray-400 py-16 text-sm">
          בחר שתי רשויות ומדד כדי להתחיל השוואה
        </div>
      )}
    </div>
  )
}
