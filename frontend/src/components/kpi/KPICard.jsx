function fmt(value, isPercentage = false) {
  if (value == null) return '—'
  if (isPercentage) {
    return Number(value).toLocaleString('he-IL', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  }
  return Math.round(value).toLocaleString('he-IL')
}

export function KPICard({ kpi, selected, onSelect }) {
  const name = kpi.name_he ?? kpi.indicator_name ?? kpi.indicator_code
  const trend = kpi.trend_pct ?? kpi.yoy_change_pct ?? null
  const trendUp = trend > 0
  const showTrend = trend != null && Math.abs(trend) >= 0.1
  const isGood = kpi.higher_is_better === false ? !trendUp : trendUp
  const trendColor = isGood ? 'text-green-600' : 'text-red-500'

  const vsNational = kpi.national_avg && kpi.national_avg !== 0
    ? ((kpi.value - kpi.national_avg) / Math.abs(kpi.national_avg) * 100).toFixed(1)
    : null

  return (
    <div
      onClick={() => onSelect(kpi.indicator_code)}
      className={`bg-white rounded-xl p-4 flex flex-col gap-1.5 cursor-pointer transition-all
        ${selected
          ? 'ring-2 ring-blue-500 shadow-md'
          : 'shadow hover:shadow-md hover:ring-1 hover:ring-blue-200'}`}
      dir="rtl"
    >
      <span className="text-xs text-gray-500 leading-tight">{name}</span>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-bold text-gray-900">
          {fmt(kpi.value, kpi.is_percentage)}
        </span>
        <span className="text-xs text-gray-400">{kpi.unit}</span>
      </div>
      {showTrend && (
        <span className={`text-xs font-medium ${trendColor}`}>
          {trendUp ? '▲' : '▼'} {Math.abs(trend).toFixed(1)}% משנה קודמת
        </span>
      )}
      {vsNational && (
        <span className="text-xs text-gray-400">
          {Number(vsNational) > 0 ? '+' : ''}{vsNational}% מהממוצע הארצי
        </span>
      )}
      {kpi.rank_national && (
        <span className="text-xs text-gray-400">דירוג ארצי: #{kpi.rank_national}</span>
      )}
    </div>
  )
}
