import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'

const CustomDot = ({ cx, cy, payload }) => {
  if (!payload?.is_forecast) return null
  return <circle key={payload.year} cx={cx} cy={cy} r={4} fill="#f59e0b" stroke="#fff" strokeWidth={1} />
}

export function ForecastChart({ data }) {
  if (!data || data.error) return null

  const lastHistoricalYear = data.historical?.at(-1)?.year

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <div className="flex items-center justify-between mb-4" dir="rtl">
        <h2 className="text-lg font-semibold text-gray-800">
          {data.indicator.name_he}
          {data.indicator.unit && (
            <span className="text-sm font-normal text-gray-400 mr-1">({data.indicator.unit})</span>
          )}
        </h2>
        {data.delta_pct !== 0 && (
          <span className={`text-sm font-medium px-2 py-0.5 rounded-full ${
            data.delta_pct > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            תרחיש: {data.delta_pct > 0 ? '+' : ''}{data.delta_pct}% לשנה
          </span>
        )}
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data.forecast} margin={{ top: 4, right: 12, left: 8, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} />
          <YAxis
            tickFormatter={v => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            formatter={v => Number(v).toLocaleString('he-IL')}
            labelFormatter={l => `שנת ${l}`}
          />
          {lastHistoricalYear && (
            <ReferenceLine
              x={lastHistoricalYear}
              stroke="#9ca3af"
              strokeDasharray="5 4"
              label={{ value: 'היום', fill: '#9ca3af', fontSize: 11 }}
            />
          )}
          <Line
            dataKey="value"
            name={data.indicator.name_he}
            stroke="#2563eb"
            strokeWidth={2}
            dot={<CustomDot />}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="flex gap-4 mt-3 text-xs text-gray-400" dir="rtl">
        <span className="flex items-center gap-1">
          <span style={{ display: 'inline-block', width: 10, height: 10, background: '#2563eb', borderRadius: '50%' }} />
          היסטוריה
        </span>
        <span className="flex items-center gap-1">
          <span style={{ display: 'inline-block', width: 10, height: 10, background: '#f59e0b', borderRadius: '50%' }} />
          תחזית
        </span>
        <span className="flex items-center gap-1">
          <span style={{ display: 'inline-block', width: 20, height: 2, background: '#9ca3af', marginTop: 4 }} />
          גבול תחזית
        </span>
        {data.base_slope !== 0 && (
          <span className="mr-auto">
            מגמה בסיסית: {data.base_slope > 0 ? '+' : ''}{Number(data.base_slope).toLocaleString('he-IL')} לשנה
          </span>
        )}
      </div>
    </div>
  )
}
