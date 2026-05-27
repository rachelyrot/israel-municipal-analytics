import { useDashboardStore } from '../../store/dashboardStore'

const DOMAIN_LABELS = {
  population:     'אוכלוסייה',
  employment:     'תעסוקה',
  education:      'חינוך',
  welfare:        'רווחה',
  budget:         'תקציב',
  infrastructure: 'תשתיות',
  taxes:          'ארנונה',
}

function fmt(value, isPercentage) {
  if (value == null) return '—'
  if (isPercentage)
    return Number(value).toLocaleString('he-IL', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'
  return Math.round(value).toLocaleString('he-IL')
}

function ValueBar({ value, nationalAvg, isPercentage, higherIsBetter }) {
  if (!isPercentage || value == null) return null
  const v = Math.min(100, Math.max(0, value))
  const av = nationalAvg != null ? Math.min(100, Math.max(0, nationalAvg)) : null
  const isAbove = av != null && value > av
  const color = av == null ? '#3b82f6'
    : higherIsBetter === false
      ? (isAbove ? '#ef4444' : '#22c55e')
      : (isAbove ? '#22c55e' : '#ef4444')

  return (
    <div className="relative h-1 bg-gray-100 rounded-full mt-1.5 mx-1">
      <div className="absolute top-0 right-0 h-full rounded-full transition-all"
        style={{ width: `${v}%`, background: color }} />
      {av != null && (
        <div className="absolute top-[-2px] h-[8px] w-[2px] bg-gray-400 rounded-full"
          style={{ right: `${av}%` }} />
      )}
    </div>
  )
}

export function KPIList({ selectedIndicator, onSelectIndicator }) {
  const { kpis, isLoadingKPIs, error } = useDashboardStore()

  if (isLoadingKPIs) return (
    <div className="bg-white rounded-xl shadow overflow-hidden">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="px-4 py-3 border-b animate-pulse flex justify-between">
          <div className="h-4 bg-gray-100 rounded w-16" />
          <div className="h-4 bg-gray-100 rounded w-28" />
        </div>
      ))}
    </div>
  )

  if (error) return (
    <div className="text-red-500 text-sm text-center py-4" dir="rtl">שגיאה: {error}</div>
  )

  if (kpis.length === 0) return (
    <div className="text-gray-400 text-sm text-center py-8" dir="rtl">אין נתונים</div>
  )

  // Group by domain, preserving insertion order
  const grouped = {}
  kpis.forEach(k => {
    ;(grouped[k.domain] ??= []).push(k)
  })

  return (
    <div className="bg-white rounded-xl shadow overflow-hidden" dir="rtl">
      {Object.entries(grouped).map(([domain, items]) => (
        <div key={domain}>
          {/* Domain header */}
          <div className="px-4 py-1.5 bg-gray-50 border-y text-xs font-semibold text-gray-500 tracking-wide">
            {DOMAIN_LABELS[domain] ?? domain}
          </div>

          {items.map(kpi => {
            const selected = selectedIndicator === kpi.indicator_code
            const hasNatAvg = kpi.national_avg != null
            const isAbove = hasNatAvg && kpi.value > kpi.national_avg
            const valueColor = !hasNatAvg ? 'text-blue-600'
              : kpi.higher_is_better === false
                ? (isAbove ? 'text-red-500' : 'text-green-600')
                : (isAbove ? 'text-green-600' : 'text-red-500')

            const trendUp = kpi.trend_pct > 0
            const showTrend = kpi.trend_pct != null && Math.abs(kpi.trend_pct) >= 0.1
            const trendGood = kpi.higher_is_better === false ? !trendUp : trendUp

            return (
              <div
                key={kpi.indicator_code}
                onClick={() => onSelectIndicator(kpi.indicator_code)}
                className={`px-4 py-2.5 border-b cursor-pointer transition-colors
                  ${selected ? 'bg-blue-50 border-r-2 border-r-blue-500' : 'hover:bg-gray-50'}`}
              >
                <div className="flex items-start justify-between gap-3">
                  {/* Left: value block */}
                  <div className="text-left min-w-[70px]">
                    <span className={`text-sm font-bold ${valueColor}`}>
                      {fmt(kpi.value, kpi.is_percentage)}
                    </span>
                    {hasNatAvg && (
                      <span className="block text-[10px] text-gray-400">
                        ממוצע: {fmt(kpi.national_avg, kpi.is_percentage)}
                      </span>
                    )}
                    {showTrend && (
                      <span className={`block text-[10px] font-medium ${trendGood ? 'text-green-500' : 'text-red-400'}`}>
                        {trendUp ? '▲' : '▼'} {Math.abs(kpi.trend_pct).toFixed(1)}%
                      </span>
                    )}
                  </div>

                  {/* Right: indicator name */}
                  <span className="text-sm text-gray-600 text-right leading-tight pt-0.5">
                    {kpi.name_he}
                  </span>
                </div>

                {/* Inline bar for percentage KPIs */}
                <ValueBar
                  value={kpi.value}
                  nationalAvg={kpi.national_avg}
                  isPercentage={kpi.is_percentage}
                  higherIsBetter={kpi.higher_is_better}
                />
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
