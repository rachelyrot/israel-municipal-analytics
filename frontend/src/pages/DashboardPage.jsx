import { useState } from 'react'
import { useDashboardStore } from '../store/dashboardStore'
import { MunicipalitySelector } from '../components/selectors/MunicipalitySelector'
import { YearSelector } from '../components/selectors/YearSelector'
import { DomainFilter } from '../components/DomainFilter'
import { KPIGrid } from '../components/kpi/KPIGrid'
import { TimeSeriesChart } from '../components/charts/TimeSeriesChart'

export function DashboardPage() {
  const { selectedMunicipality, selectedYear, kpis } = useDashboardStore()
  const [selectedIndicator, setSelectedIndicator] = useState(null)

  const selectedKPI = kpis.find(k => k.indicator_code === selectedIndicator)

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex gap-3 items-center flex-wrap sticky top-0 z-40 shadow-sm">
        <h1 className="text-lg font-bold text-gray-800 ml-auto whitespace-nowrap">
          ניתוח רשויות מקומיות 🏙️
        </h1>
        <MunicipalitySelector />
        <YearSelector />
      </header>

      <main className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
        {/* מצב ריק */}
        {!selectedMunicipality && (
          <div className="flex flex-col items-center justify-center mt-32 gap-3 text-center">
            <span className="text-5xl">🗺️</span>
            <p className="text-xl text-gray-500">בחר רשות מקומית להתחיל</p>
            <p className="text-sm text-gray-400">נתוני הלמ"ס 1999–2023 · 256 רשויות · 40+ מדדים</p>
          </div>
        )}

        {selectedMunicipality && (
          <>
            {/* כותרת רשות */}
            <div className="flex items-end gap-3" dir="rtl">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedMunicipality.name}</h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  {selectedMunicipality.municipality_type} · {selectedMunicipality.district} · שנת {selectedYear}
                </p>
              </div>
            </div>

            {/* סינון תחום */}
            <DomainFilter />

            {/* כרטיסי KPI */}
            <KPIGrid
              selectedIndicator={selectedIndicator}
              onSelectIndicator={code => setSelectedIndicator(prev => prev === code ? null : code)}
            />

            {/* גרף */}
            {selectedIndicator && selectedKPI && (
              <div className="bg-white rounded-xl shadow p-6">
                <div className="flex justify-between items-start mb-4" dir="rtl">
                  <div>
                    <h3 className="font-semibold text-gray-800">{selectedKPI.name_he}</h3>
                    <p className="text-xs text-gray-400">לחץ על כרטיס אחר לשינוי · לחץ שוב לסגירה</p>
                  </div>
                  <button
                    onClick={() => setSelectedIndicator(null)}
                    className="text-gray-400 hover:text-gray-600 text-xl leading-none"
                  >×</button>
                </div>
                <TimeSeriesChart
                  indicatorCode={selectedIndicator}
                  municipalityName={selectedMunicipality.name}
                  unit={selectedKPI.unit}
                />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
