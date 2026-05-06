import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#d97706']

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
export function CompareChart({ data }) {
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

  if (national_avg) {
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
      <h2 className="text-lg font-semibold mb-4" dir="rtl">
        {indicator?.name_he}
        {unit && <span className="text-sm text-gray-400 mr-2">({unit})</span>}
      </h2>
      <ResponsiveContainer width="100%" height={320}>
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
          {national_avg && national_avg.length > 0 && (
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
