import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed', '#0891b2', '#db2777', '#ea580c']

/**
 * CompareChart — renders municipality comparison as overlaid line series.
 *
 * Expected prop shape:
 *   data: {
 *     indicator: { name_he, unit },
 *     municipalities: [{ id, name, series: [{ year, value }] }],
 *     national_avg: [{ year, avg_value }]
 *   }
 */
export function CompareChart({ data, height = 320 }) {
  const [showNationalAvg, setShowNationalAvg] = useState(true)

  if (!data) return null

  const { indicator, municipalities, national_avg } = data

  // Merge all series into one array of { year, <municipalityName>, "ממוצע ארצי" }
  const byYear = {}

  municipalities.forEach(m => {
    m.series.forEach(({ year, value }) => {
      if (value == null) return
      if (!byYear[year]) byYear[year] = { year }
      byYear[year][m.name] = value
    })
  })

  if (showNationalAvg && national_avg) {
    national_avg.forEach(({ year, avg_value }) => {
      if (avg_value == null) return
      if (!byYear[year]) byYear[year] = { year }
      byYear[year]['ממוצע ארצי'] = avg_value
    })
  }

  const chartData = Object.values(byYear).sort((a, b) => a.year - b.year)

  const fmt = (v) => v != null ? v.toLocaleString('he-IL') : ''
  const unit = indicator?.unit ?? ''

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex items-start justify-between mb-4" dir="rtl">
        <h2 className="text-lg font-semibold">
          {indicator?.name_he}
          {unit && <span className="text-sm text-gray-400 mr-2">({unit})</span>}
        </h2>
        {national_avg && national_avg.length > 0 && (
          <button
            onClick={() => setShowNationalAvg(v => !v)}
            className={`flex-shrink-0 flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-150 ${
              showNationalAvg
                ? 'bg-slate-100 border-slate-300 text-slate-600 hover:bg-slate-200'
                : 'bg-white border-slate-200 text-slate-300 hover:border-slate-300 hover:text-slate-400'
            }`}
          >
            <svg width="16" height="8" viewBox="0 0 16 8" className="flex-shrink-0">
              <line x1="0" y1="4" x2="16" y2="4"
                stroke={showNationalAvg ? '#9ca3af' : '#e2e8f0'}
                strokeWidth="2" strokeDasharray="4 3" />
            </svg>
            ממוצע ארצי
          </button>
        )}
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} width={75} />
          <Tooltip
            formatter={(v, name) => [fmt(v) + (unit ? ` ${unit}` : ''), name]}
            labelFormatter={l => `שנת ${l}`}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {municipalities.map((m, i) => (
            <Line
              key={m.id}
              dataKey={m.name}
              stroke={COLORS[i % COLORS.length]}
              strokeWidth={2.5}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}

            />
          ))}
          {showNationalAvg && national_avg && national_avg.length > 0 && (
            <Line
              dataKey="ממוצע ארצי"
              stroke="#9ca3af"
              strokeDasharray="5 5"
              strokeWidth={1.5}
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
