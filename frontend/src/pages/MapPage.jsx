import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { ChoroplethMap } from '../components/maps/ChoroplethMap'

function fmt(value, isPercentage = false) {
  if (value == null) return 'אין נתון'
  if (isPercentage) {
    return Number(value).toLocaleString('he-IL', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  }
  return Math.round(value).toLocaleString('he-IL')
}

export function MapPage() {
  const [indicators, setIndicators] = useState({})
  const [indicatorCode, setIndicatorCode] = useState('POP_TOTAL')
  const [year, setYear] = useState(2024)
  const [geojson, setGeojson] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selected, setSelected] = useState(null)
  const isPercentage = geojson?.metadata?.is_percentage ?? false

  useEffect(() => {
    api.getIndicators().then(setIndicators)
  }, [])

  useEffect(() => {
    if (!indicatorCode) return
    setLoading(true)
    api.getChoroplethGeoJSON(indicatorCode, year)
      .then(setGeojson)
      .finally(() => setLoading(false))
  }, [indicatorCode, year])

  const indicatorName = Object.values(indicators).flat()
    .find(i => i.code === indicatorCode)?.name_he || indicatorCode

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 48px)' }} dir="rtl">
      {/* Toolbar */}
      <div className="bg-white border-b px-4 py-2 flex gap-3 items-center flex-shrink-0">
        <h1 className="text-lg font-bold text-gray-800">מפת רשויות</h1>

        <select
          value={indicatorCode}
          onChange={e => setIndicatorCode(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          {Object.entries(indicators).map(([domain, inds]) => (
            <optgroup key={domain} label={domain}>
              {inds.map(ind => (
                <option key={ind.code} value={ind.code}>{ind.name_he}</option>
              ))}
            </optgroup>
          ))}
        </select>

        <select
          value={year}
          onChange={e => setYear(Number(e.target.value))}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          {Array.from({ length: 26 }, (_, i) => 2024 - i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        {loading && <span className="text-sm text-gray-400">טוען...</span>}

        {geojson && (
          <span className="text-xs text-gray-400 mr-auto">
            {geojson.metadata?.count || 0} רשויות · {indicatorName} · {year}
          </span>
        )}
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Map */}
        <div className="flex-1">
          {geojson ? (
            <ChoroplethMap geojson={geojson} isPercentage={isPercentage} onMunicipalityClick={setSelected} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              {loading ? 'טוען מפה...' : 'אין נתונים — הריצו את סקריפט seed_coordinates.py תחילה'}
            </div>
          )}
        </div>

        {/* Side panel — shown when municipality clicked */}
        {selected && (
          <div className="w-64 bg-white border-r shadow-inner p-4 overflow-y-auto flex-shrink-0">
            <div className="flex justify-between items-start mb-3">
              <h2 className="font-bold text-gray-800">{selected.municipality_name}</h2>
              <button
                onClick={() => setSelected(null)}
                className="text-gray-400 hover:text-gray-600 text-lg leading-none"
              >×</button>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">מחוז</span>
                <span>{selected.district || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">סוג</span>
                <span>{selected.municipality_type || '—'}</span>
              </div>
              <div className="flex justify-between border-t pt-2 mt-2">
                <span className="text-gray-500">{indicatorName}</span>
                <span className="font-semibold text-blue-700">
                  {fmt(selected.value, isPercentage)}
                </span>
              </div>
              {selected.national_avg != null && (
                <div className="flex justify-between">
                  <span className="text-gray-500">ממוצע ארצי</span>
                  <span>{fmt(selected.national_avg, isPercentage)}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      {geojson && (
        <div className="bg-white border-t px-4 py-2 flex items-center gap-3 flex-shrink-0">
          <span className="text-xs text-gray-500">ערך נמוך</span>
          {['#eff3ff', '#bdd7e7', '#6baed6', '#2171b5', '#084594'].map(c => (
            <div key={c} style={{ background: c, width: 28, height: 14, borderRadius: 3 }} />
          ))}
          <span className="text-xs text-gray-500">ערך גבוה</span>
          <span className="text-xs text-gray-400 mr-2">(5 דליים קוונטיל)</span>
          <div className="flex items-center gap-1 mr-4">
            <div style={{ background: '#d1d5db', width: 12, height: 12, borderRadius: '50%' }} />
            <span className="text-xs text-gray-400">אין נתון</span>
          </div>
        </div>
      )}
    </div>
  )
}
