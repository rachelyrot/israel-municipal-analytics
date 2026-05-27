import { useState, useEffect, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useDashboardStore } from '../store/dashboardStore'
import { RankingsList } from '../components/RankingsList'
import { MunicipalityProfile } from '../components/MunicipalityProfile'
import { ChoroplethMap } from '../components/maps/ChoroplethMap'
import { api } from '../api/client'

const VIRIDIS = ['#440154', '#3e4989', '#26828e', '#6ece58', '#fde725']
const YEARS = Array.from({ length: 26 }, (_, i) => 1999 + i)

const DOMAIN_HE = {
  population: 'אוכלוסייה',
  employment: 'תעסוקה',
  education: 'חינוך',
  welfare: 'רווחה',
  budget: 'תקציב',
  infrastructure: 'תשתיות',
  land: 'קרקע',
  health: 'בריאות',
  arnona: 'ארנונה',
  cluster: 'אשכול סוציו-אקונומי',
  construction: 'בנייה',
  transport: 'תחבורה',
  social: 'רווחה חברתית',
}

function IndicatorSearch({ allIndicators, value, onChange }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [dropPos, setDropPos] = useState({ top: 0, left: 0, width: 256 })
  const btnRef = useRef(null)
  const inputRef = useRef(null)

  const allFlat = Object.entries(allIndicators).flatMap(([domain, inds]) =>
    inds.map(i => ({ ...i, domain }))
  )
  const filtered = query.trim()
    ? allFlat.filter(i => i.name_he.includes(query.trim()))
    : allFlat
  const current = allFlat.find(i => i.code === value)

  function openDropdown() {
    const rect = btnRef.current?.getBoundingClientRect()
    if (rect) setDropPos({ top: rect.bottom + 4, left: rect.left, width: 256 })
    setQuery('')
    setOpen(true)
    setTimeout(() => inputRef.current?.focus(), 0)
  }

  function select(code) {
    onChange(code)
    setOpen(false)
    setQuery('')
  }

  return (
    <>
      <div ref={btnRef} className="flex items-center gap-1.5 border border-slate-200 rounded-md px-3 py-1 bg-white shadow-sm cursor-pointer" onClick={openDropdown}>
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">צבע המפה</span>
        <span className="w-48 text-xs font-medium text-slate-700 truncate">{current?.name_he || '—'}</span>
        <span className="text-[10px] text-slate-400">▾</span>
      </div>

      {open && createPortal(
        <>
          <div className="fixed inset-0 z-[9998]" onClick={() => setOpen(false)} />
          <div
            className="fixed bg-white border border-slate-200 rounded-lg shadow-xl z-[9999] flex flex-col"
            style={{ top: dropPos.top, left: dropPos.left, width: dropPos.width }}
            dir="rtl"
          >
            <input
              ref={inputRef}
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="חיפוש מדד..."
              className="text-sm px-3 py-2.5 border-b border-slate-100 focus:outline-none rounded-t-lg w-full"
            />
            <div className="overflow-y-auto max-h-72">
              {filtered.length === 0
                ? <p className="text-sm text-slate-400 px-3 py-2">לא נמצא</p>
                : filtered.map(i => (
                  <div
                    key={i.code}
                    onClick={() => select(i.code)}
                    className={`text-right text-sm px-3 py-2 cursor-pointer hover:bg-slate-50 truncate ${i.code === value ? 'bg-blue-50 text-blue-700 font-medium' : 'text-slate-700'}`}
                  >
                    <span className="text-[10px] text-slate-400 ml-1">{DOMAIN_HE[i.domain] || i.domain}</span>
                    {i.name_he}
                  </div>
                ))
              }
            </div>
          </div>
        </>,
        document.body
      )}
    </>
  )
}

export function DashboardPage() {
  const { selectedMunicipality, selectedYear, setMunicipality, setYear } = useDashboardStore()

  const [allIndicators, setAllIndicators] = useState({})
  const [mapIndicatorCode, setMapIndicatorCode] = useState('HEALTH_CANCER_RATE_MEN')
  const [geojson, setGeojson] = useState(null)
  const [mapLoading, setMapLoading] = useState(false)

  const isPercentage = geojson?.metadata?.is_percentage ?? false
  const currentIndicator = Object.values(allIndicators).flat().find(i => i.code === mapIndicatorCode)
  const mapIndicatorName = currentIndicator?.name_he || ''
  const mapIndicatorUnit = currentIndicator?.unit || ''

  useEffect(() => {
    api.getIndicators(selectedYear).then(data => {
      setAllIndicators(data)
      const allCodes = Object.values(data).flat().map(i => i.code)
      if (allCodes.length > 0 && !allCodes.includes(mapIndicatorCode)) {
        setMapIndicatorCode(allCodes[0])
      }
    })
  }, [selectedYear])

  useEffect(() => {
    if (!mapIndicatorCode) return
    setMapLoading(true)
    api.getChoroplethGeoJSON(mapIndicatorCode, selectedYear)
      .then(setGeojson)
      .catch(() => setGeojson(null))
      .finally(() => setMapLoading(false))
  }, [mapIndicatorCode, selectedYear])

  const handleMapClick = useCallback(async (props) => {
    try {
      if (props.municipality_id) {
        const muni = await api.getMunicipality(props.municipality_id)
        setMunicipality(muni)
      } else if (props.municipality_name) {
        const results = await api.searchMunicipalities(props.municipality_name)
        if (results.length > 0) setMunicipality(results[0])
      }
    } catch {}
  }, [setMunicipality])

  return (
    <div className="h-screen flex flex-col bg-slate-100" dir="rtl">
      <div className="flex flex-1 overflow-hidden gap-10 p-10">

        {/* ── RIGHT: Map ── */}
        <div className="flex-1 flex flex-col relative rounded-xl shadow-sm">

          {/* Toolbar — no overflow-hidden so dropdown can escape */}
          <div className="bg-white shadow-sm px-4 py-2 flex items-center justify-end gap-2 flex-shrink-0 z-20 relative rounded-t-xl">
            {/* Loading pill */}
            {mapLoading && (
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                טוען...
              </span>
            )}

            {/* Year selector */}
            <div className="flex items-center gap-1.5 border border-slate-200 rounded-md px-3 py-1 bg-white shadow-sm">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">שנה</span>
              <select
                value={selectedYear}
                onChange={e => setYear(Number(e.target.value))}
                className="text-xs font-semibold text-slate-700 bg-transparent focus:outline-none cursor-pointer"
              >
                {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>

            {/* Indicator selector */}
            <IndicatorSearch
              allIndicators={allIndicators}
              value={mapIndicatorCode}
              onChange={setMapIndicatorCode}
            />
          </div>

          {/* Map */}
          <div className="flex-1 relative overflow-hidden rounded-b-xl">
            {geojson ? (
              <ChoroplethMap
                geojson={geojson}
                isPercentage={isPercentage}
                unit={mapIndicatorUnit}
                onMunicipalityClick={handleMapClick}
                selectedMunicipalityId={selectedMunicipality?.id}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-1.5 text-slate-400">
                <span className="text-2xl">🗺️</span>
                <span className="text-xs">
                  {mapLoading ? 'טוען מפה...' : 'אין נתונים — הריצו seed_coordinates.py'}
                </span>
              </div>
            )}

            {/* Legend overlay */}
            {geojson && !mapLoading && (
              <div
                className="absolute bottom-4 left-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-md px-3 py-2 z-[1000] min-w-[130px]"
                dir="rtl"
              >
                <p className="text-[10px] font-semibold text-slate-600 mb-1.5 truncate max-w-[120px]">
                  {mapIndicatorName}
                </p>
                <div className="flex items-center gap-1">
                  <span className="text-[9px] text-slate-400">נמוך</span>
                  <div className="flex rounded-full overflow-hidden flex-1">
                    {VIRIDIS.map(c => (
                      <div key={c} style={{ background: c, height: 6, flex: 1 }} />
                    ))}
                  </div>
                  <span className="text-[9px] text-slate-400">גבוה</span>
                </div>
                <div className="flex items-center gap-1 mt-1">
                  <div className="w-2 h-2 rounded-full bg-slate-300 flex-shrink-0" />
                  <span className="text-[9px] text-slate-400">אין נתון</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── LEFT: Rankings / Profile ── */}
        <div className="w-[360px] flex-shrink-0 bg-white shadow-sm rounded-xl flex flex-col overflow-hidden">
          {selectedMunicipality
            ? <MunicipalityProfile />
            : <RankingsList mapIndicatorCode={mapIndicatorCode} />
          }
        </div>

      </div>
    </div>
  )
}
