import { useState, useEffect } from 'react'
import { LocalMunicipalitySelector } from '../components/selectors/LocalMunicipalitySelector'
import { ForecastChart } from '../components/charts/ForecastChart'
import { api } from '../api/client'

export function ForecastPage() {
  const [muni, setMuni] = useState(null)
  const [indicators, setIndicators] = useState({})
  const [indicatorCode, setIndicatorCode] = useState('POP_TOTAL')
  const [deltaPct, setDeltaPct] = useState(0)
  const [yearsAhead, setYearsAhead] = useState(5)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getIndicators().then(setIndicators)
  }, [])

  useEffect(() => {
    if (!muni || !indicatorCode) return
    setLoading(true)
    api.getForecast(muni.id, indicatorCode, deltaPct, yearsAhead)
      .then(setData)
      .finally(() => setLoading(false))
  }, [muni, indicatorCode, deltaPct, yearsAhead])

  return (
    <div className="p-6 max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">תחזיות What-If</h1>
      <p className="text-sm text-gray-500 mb-6">
        בחר רשות ומדד, גרור את הסליידר לסימולציית שינוי שנתי נוסף
      </p>

      {/* Selectors */}
      <div className="bg-white rounded-xl shadow p-4 flex gap-4 flex-wrap items-end mb-4">
        <div className="flex-1 min-w-52">
          <label className="text-xs text-gray-500 block mb-1">רשות</label>
          <LocalMunicipalitySelector value={muni} onChange={setMuni} />
        </div>
        <div className="flex-1 min-w-52">
          <label className="text-xs text-gray-500 block mb-1">מדד</label>
          <select
            value={indicatorCode}
            onChange={e => setIndicatorCode(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 bg-white text-sm"
          >
            {Object.entries(indicators).map(([domain, inds]) => (
              <optgroup key={domain} label={domain}>
                {inds.map(ind => (
                  <option key={ind.code} value={ind.code}>{ind.name_he}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">שנות תחזית</label>
          <select
            value={yearsAhead}
            onChange={e => setYearsAhead(Number(e.target.value))}
            className="border rounded-lg px-3 py-2 bg-white text-sm"
          >
            {[3, 5, 10].map(y => (
              <option key={y} value={y}>{y} שנים</option>
            ))}
          </select>
        </div>
      </div>

      {/* Delta slider */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">שינוי שנתי נוסף מעבר למגמה</label>
          <span className={`font-bold text-lg tabular-nums ${
            deltaPct > 0 ? 'text-green-600' : deltaPct < 0 ? 'text-red-600' : 'text-gray-500'
          }`}>
            {deltaPct > 0 ? '+' : ''}{deltaPct}%
          </span>
        </div>
        <input
          type="range"
          min="-10"
          max="10"
          step="0.5"
          value={deltaPct}
          onChange={e => setDeltaPct(Number(e.target.value))}
          className="w-full accent-blue-600"
          dir="ltr"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1" dir="ltr">
          <span>-10%</span>
          <span>0% (מגמה בלבד)</span>
          <span>+10%</span>
        </div>
        {deltaPct !== 0 && (
          <button
            onClick={() => setDeltaPct(0)}
            className="mt-2 text-xs text-blue-500 hover:text-blue-700"
          >
            אפס תרחיש
          </button>
        )}
      </div>

      {/* Chart */}
      {loading && (
        <div className="text-center text-gray-400 py-12">טוען תחזית...</div>
      )}
      {!loading && data?.error && (
        <div className="text-center text-red-500 py-8">{data.error}</div>
      )}
      {!loading && data && !data.error && (
        <ForecastChart data={data} />
      )}
      {!muni && (
        <div className="text-center text-gray-300 py-16 text-lg">
          בחר רשות מקומית להצגת תחזית
        </div>
      )}
    </div>
  )
}
