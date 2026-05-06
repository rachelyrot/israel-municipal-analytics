import { useState, useEffect } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { api } from '../../api/client'
import { useDashboardStore } from '../../store/dashboardStore'

export function TimeSeriesChart({ indicatorCode, municipalityName, unit }) {
  const { selectedMunicipality } = useDashboardStore()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedMunicipality || !indicatorCode) return
    setLoading(true)
    api.getTimeSeries(selectedMunicipality.id, indicatorCode)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false))
  }, [selectedMunicipality, indicatorCode])

  if (loading) return (
    <div className="h-64 flex items-center justify-center text-gray-400 text-sm">טוען גרף...</div>
  )

  if (data.length === 0) return (
    <div className="h-64 flex items-center justify-center text-gray-400 text-sm" dir="rtl">
      אין נתונים לאורך זמן
    </div>
  )

  const fmt = (v) => v != null ? v.toLocaleString('he-IL') : ''
  const chartData = data.filter(d => d.value != null)

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="year" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={fmt} tick={{ fontSize: 11 }} width={70} />
        <Tooltip
          formatter={(v, name) => [fmt(v) + (unit ? ` ${unit}` : ''), name]}
          labelFormatter={l => `שנת ${l}`}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line
          dataKey="value"
          name={municipalityName}
          stroke="#2563eb"
          strokeWidth={2.5}
          dot={{ r: 3 }}
          activeDot={{ r: 5 }}
        />
        <Line
          dataKey="national_avg"
          name="ממוצע ארצי"
          stroke="#9ca3af"
          strokeDasharray="5 5"
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
