import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

const getMuniColor = (i) => `hsl(${Math.round((i * 137.508 + 220) % 360)}, 65%, 48%)`
const DISTRICT_COLORS = ['#f59e0b', '#10b981', '#8b5cf6', '#06b6d4', '#f97316']
const TYPE_COLORS = ['#e11d48', '#0284c7', '#7c3aed']

function ToggleBtn({ label, color, dashed, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border transition-all"
      style={{
        borderColor: active ? color : '#d1d5db',
        backgroundColor: active ? color + '18' : '#f9fafb',
        color: active ? color : '#9ca3af',
        opacity: active ? 1 : 0.6,
      }}
    >
      <span style={{
        display: 'inline-block', width: 18, height: 2,
        background: active ? color : '#d1d5db',
        borderTop: dashed ? `2px dashed ${active ? color : '#d1d5db'}` : undefined,
        backgroundColor: dashed ? 'transparent' : (active ? color : '#d1d5db'),
        flexShrink: 0,
      }} />
      {label}
    </button>
  )
}

export function CompareChart({ data, height = 300 }) {
  const [hidden, setHidden] = useState(new Set())

  if (!data) return null

  const { indicator, municipalities, national_avg, district_avgs, type_avgs } = data

  const toggle = (key) => setHidden(prev => {
    const next = new Set(prev)
    if (next.has(key)) next.delete(key)
    else next.add(key)
    return next
  })

  const byYear = {}

  municipalities.forEach(m => {
    m.series.forEach(({ year, value }) => {
      if (value == null) return
      if (!byYear[year]) byYear[year] = { year }
      byYear[year][m.name] = value
    })
  })

  if (national_avg) {
    national_avg.forEach(({ year, avg_value }) => {
      if (avg_value == null) return
      if (!byYear[year]) byYear[year] = { year }
      byYear[year]['ממוצע ארצי'] = avg_value
    })
  }

  if (district_avgs) {
    district_avgs.forEach(({ district, series }) => {
      const key = `ממוצע מחוז ${district}`
      series.forEach(({ year, avg_value }) => {
        if (avg_value == null) return
        if (!byYear[year]) byYear[year] = { year }
        byYear[year][key] = avg_value
      })
    })
  }

  if (type_avgs) {
    type_avgs.forEach(({ municipality_type, series }) => {
      const key = `ממוצע ${municipality_type}`
      series.forEach(({ year, avg_value }) => {
        if (avg_value == null) return
        if (!byYear[year]) byYear[year] = { year }
        byYear[year][key] = avg_value
      })
    })
  }

  const chartData = Object.values(byYear).sort((a, b) => a.year - b.year)
  const fmt = (v) => v != null ? v.toLocaleString('he-IL') : ''
  const unit = indicator?.unit ?? ''

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <h2 className="text-base font-semibold mb-3" dir="rtl">
        {indicator?.name_he}
        {unit && <span className="text-xs text-gray-400 mr-2">({unit})</span>}
      </h2>

      {/* Toggle buttons */}
      <div className="flex flex-wrap gap-1.5 mb-3" dir="rtl">
        {municipalities.map((m, i) => (
          <ToggleBtn
            key={m.id}
            label={m.name}
            color={getMuniColor(i)}
            dashed={false}
            active={!hidden.has(m.name)}
            onClick={() => toggle(m.name)}
          />
        ))}
        {district_avgs && district_avgs.map((d, i) => {
          const key = `ממוצע מחוז ${d.district}`
          return (
            <ToggleBtn
              key={key}
              label={key}
              color={DISTRICT_COLORS[i % DISTRICT_COLORS.length]}
              dashed
              active={!hidden.has(key)}
              onClick={() => toggle(key)}
            />
          )
        })}
        {type_avgs && type_avgs.map((t, i) => {
          const key = `ממוצע ${t.municipality_type}`
          return (
            <ToggleBtn
              key={key}
              label={key}
              color={TYPE_COLORS[i % TYPE_COLORS.length]}
              dashed
              active={!hidden.has(key)}
              onClick={() => toggle(key)}
            />
          )
        })}
        {national_avg && national_avg.length > 0 && (
          <ToggleBtn
            label="ממוצע ארצי"
            color="#9ca3af"
            dashed
            active={!hidden.has('ממוצע ארצי')}
            onClick={() => toggle('ממוצע ארצי')}
          />
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
          {municipalities.map((m, i) => (
            <Line
              key={m.id}
              dataKey={m.name}
              stroke={getMuniColor(i)}
              strokeWidth={2.5}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
              hide={hidden.has(m.name)}
            />
          ))}
          {district_avgs && district_avgs.map((d, i) => (
            <Line
              key={`district-${d.district}`}
              dataKey={`ממוצע מחוז ${d.district}`}
              stroke={DISTRICT_COLORS[i % DISTRICT_COLORS.length]}
              strokeDasharray="8 3"
              strokeWidth={1.5}
              dot={false}
              hide={hidden.has(`ממוצע מחוז ${d.district}`)}
            />
          ))}
          {type_avgs && type_avgs.map((t, i) => (
            <Line
              key={`type-${t.municipality_type}`}
              dataKey={`ממוצע ${t.municipality_type}`}
              stroke={TYPE_COLORS[i % TYPE_COLORS.length]}
              strokeDasharray="3 3"
              strokeWidth={1.5}
              dot={false}
              hide={hidden.has(`ממוצע ${t.municipality_type}`)}
            />
          ))}
          {national_avg && national_avg.length > 0 && (
            <Line
              dataKey="ממוצע ארצי"
              stroke="#9ca3af"
              strokeDasharray="5 5"
              strokeWidth={1.5}
              dot={false}
              hide={hidden.has('ממוצע ארצי')}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
