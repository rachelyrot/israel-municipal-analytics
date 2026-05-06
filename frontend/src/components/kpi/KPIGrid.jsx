import { useDashboardStore } from '../../store/dashboardStore'
import { KPICard } from './KPICard'

export function KPIGrid({ selectedIndicator, onSelectIndicator }) {
  const { kpis, isLoadingKPIs, error } = useDashboardStore()

  if (isLoadingKPIs) return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl p-4 h-28 animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-3/4 mb-3" />
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-2" />
          <div className="h-3 bg-gray-100 rounded w-2/3" />
        </div>
      ))}
    </div>
  )

  if (error) return (
    <div className="text-red-500 text-sm text-center py-4" dir="rtl">שגיאה: {error}</div>
  )

  if (kpis.length === 0) return (
    <div className="text-gray-400 text-sm text-center py-8" dir="rtl">אין נתונים לתחום זה</div>
  )

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {kpis.map(kpi => (
        <KPICard
          key={kpi.indicator_code}
          kpi={kpi}
          selected={selectedIndicator === kpi.indicator_code}
          onSelect={onSelectIndicator}
        />
      ))}
    </div>
  )
}
