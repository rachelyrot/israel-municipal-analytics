import { useState, useEffect } from 'react'
import { api } from '../api/client'

const DISTRICTS = ['כל המחוזות', 'תל אביב', 'ירושלים', 'חיפה', 'מרכז', 'דרום', 'צפון', 'יהודה ושומרון']

export function RankingsPage() {
  const [indicators, setIndicators] = useState([])
  const [indicatorCode, setIndicatorCode] = useState('')
  const [year, setYear] = useState(2022)
  const [district, setDistrict] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.getIndicators().then(setIndicators) }, [])

  const load = async () => {
    if (!indicatorCode) return
    setLoading(true)
    try {
      const result = await api.getRankings(indicatorCode, year, district || null)
      setData(result)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">דירוגי רשויות</h1>

      <div className="bg-white rounded-xl shadow p-4 flex gap-3 flex-wrap items-end mb-6">
        <select
          value={indicatorCode}
          onChange={e => setIndicatorCode(e.target.value)}
          className="border rounded-lg px-3 py-2 bg-white flex-1 min-w-48"
        >
          <option value="">בחר מדד</option>
          {indicators.flatMap(d =>
            d.indicators
              ? d.indicators.map(ind => (
                  <option key={ind.code} value={ind.code}>{ind.name_he}</option>
                ))
              : []
          )}
        </select>

        <select
          value={year}
          onChange={e => setYear(Number(e.target.value))}
          className="border rounded-lg px-3 py-2 bg-white"
        >
          {Array.from({ length: 25 }, (_, i) => 2023 - i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        <select
          value={district}
          onChange={e => setDistrict(e.target.value)}
          className="border rounded-lg px-3 py-2 bg-white"
        >
          {DISTRICTS.map(d => (
            <option key={d} value={d === 'כל המחוזות' ? '' : d}>{d}</option>
          ))}
        </select>

        <button
          onClick={load}
          disabled={!indicatorCode}
          className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          הצג דירוג
        </button>
      </div>

      {loading && (
        <div className="text-center text-gray-400 py-12">טוען...</div>
      )}

      {!loading && data && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="px-4 py-3 border-b text-sm text-gray-500">
            {data.indicator.name_he}
            {data.indicator.unit ? ` (${data.indicator.unit})` : ''} · {year} · {data.total} רשויות
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-2 text-right">דירוג</th>
                <th className="px-4 py-2 text-right">רשות</th>
                <th className="px-4 py-2 text-right">מחוז</th>
                <th className="px-4 py-2 text-right">ערך</th>
              </tr>
            </thead>
            <tbody>
              {data.rankings.map(r => (
                <tr key={r.municipality_id} className="border-t hover:bg-blue-50 transition-colors">
                  <td className="px-4 py-2 text-gray-400 font-mono">#{r.rank}</td>
                  <td className="px-4 py-2 font-medium">{r.name}</td>
                  <td className="px-4 py-2 text-gray-500">{r.district || '—'}</td>
                  <td className="px-4 py-2 font-semibold">
                    {typeof r.value === 'number'
                      ? r.value.toLocaleString('he-IL')
                      : r.value}
                    {data.indicator.unit && (
                      <span className="text-xs text-gray-400 mr-1">{data.indicator.unit}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
