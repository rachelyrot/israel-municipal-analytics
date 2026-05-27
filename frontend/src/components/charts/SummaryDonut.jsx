import { PieChart, Pie, Cell, Tooltip } from 'recharts'

function classify(kpi) {
  if (kpi.value == null || !kpi.national_avg) return null
  const dev = (kpi.value - kpi.national_avg) / Math.abs(kpi.national_avg)
  const normalized = kpi.higher_is_better === false ? -dev : dev
  if (normalized > 0.08) return 'above'
  if (normalized < -0.08) return 'below'
  return 'around'
}

const SEGMENTS = [
  { key: 'above', label: 'מעל הממוצע', color: '#22c55e' },
  { key: 'around', label: 'סביב הממוצע', color: '#f59e0b' },
  { key: 'below', label: 'מתחת לממוצע', color: '#ef4444' },
]

export function SummaryDonut({ kpis }) {
  const withData = kpis.filter(k => k.value != null && k.national_avg != null)
  if (withData.length === 0) return null

  const counts = { above: 0, around: 0, below: 0 }
  withData.forEach(k => { const c = classify(k); if (c) counts[c]++ })

  const score = Math.round((counts.above / withData.length) * 100)
  const data = SEGMENTS.map(s => ({ ...s, value: counts[s.key] })).filter(d => d.value > 0)

  return (
    <div className="bg-white rounded-xl shadow p-4 flex items-center gap-5" dir="rtl">
      {/* Donut */}
      <div className="relative flex-shrink-0">
        <PieChart width={110} height={110}>
          <Pie
            data={data}
            cx={50} cy={50}
            innerRadius={33} outerRadius={50}
            startAngle={90} endAngle={-270}
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((d, i) => <Cell key={i} fill={d.color} />)}
          </Pie>
          <Tooltip
            formatter={(v, name) => [v + ' מדדים', name]}
            contentStyle={{ direction: 'rtl', fontSize: 12 }}
          />
        </PieChart>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-xl font-bold text-gray-800">{score}%</span>
          <span className="text-[9px] text-gray-400 leading-tight">ביצועים</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-col gap-2 min-w-0">
        <p className="text-xs font-semibold text-gray-600">מדדים ביחס לממוצע הארצי</p>
        {SEGMENTS.map(({ key, label, color }) => counts[key] > 0 && (
          <div key={key} className="flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
            <span className="text-gray-500">{label}</span>
            <span className="font-bold mr-auto" style={{ color }}>{counts[key]}</span>
          </div>
        ))}
        <p className="text-[10px] text-gray-300 mt-1">מתוך {withData.length} מדדים</p>
      </div>
    </div>
  )
}
