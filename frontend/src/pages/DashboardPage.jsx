import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useDashboardStore } from '../store/dashboardStore'
import { RankingsList } from '../components/RankingsList'
import { MunicipalityProfile } from '../components/MunicipalityProfile'
import { api } from '../api/client'

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
  cluster: 'אשכול',
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
    if (rect) setDropPos({ top: rect.bottom + 4, left: rect.left, width: 272 })
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
      <div
        ref={btnRef}
        className="flex items-center gap-1.5 border border-slate-200 rounded-md px-3 py-1.5 bg-white shadow-sm cursor-pointer hover:border-slate-300"
        onClick={openDropdown}
      >
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">מדד לדירוג</span>
        <span className="w-44 text-xs font-medium text-slate-700 truncate">{current?.name_he || '—'}</span>
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
  const [rankingIndicatorCode, setRankingIndicatorCode] = useState('POP_TOTAL')

  useEffect(() => {
    api.getIndicators(selectedYear).then(data => {
      setAllIndicators(data)
      const allCodes = Object.values(data).flat().map(i => i.code)
      if (allCodes.length > 0 && !allCodes.includes(rankingIndicatorCode)) {
        setRankingIndicatorCode(allCodes[0])
      }
    })
  }, [selectedYear])

  return (
    <div className="h-screen flex flex-col bg-slate-100" dir="rtl">

      {/* ── Toolbar ── */}
      <div className="bg-white border-b px-4 py-2 flex items-center justify-end gap-2 flex-shrink-0 z-20 relative shadow-sm">
        <div className="flex items-center gap-1.5 border border-slate-200 rounded-md px-3 py-1.5 bg-white shadow-sm">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">שנה</span>
          <select
            value={selectedYear}
            onChange={e => setYear(Number(e.target.value))}
            className="text-xs font-semibold text-slate-700 bg-transparent focus:outline-none cursor-pointer"
          >
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>

        <IndicatorSearch
          allIndicators={allIndicators}
          value={rankingIndicatorCode}
          onChange={setRankingIndicatorCode}
        />

        {selectedMunicipality && (
          <button
            onClick={() => setMunicipality(null)}
            className="text-xs text-slate-400 hover:text-red-400 border border-slate-200 rounded-md px-2.5 py-1.5 hover:border-red-300 transition"
          >
            ✕ נקה בחירה
          </button>
        )}
      </div>

      {/* ── Main panels ── */}
      <div className="flex flex-1 overflow-hidden gap-4 p-4">

        {/* Rankings panel */}
        <div className="w-[340px] flex-shrink-0 bg-white shadow-sm rounded-xl flex flex-col overflow-hidden">
          <RankingsList mapIndicatorCode={rankingIndicatorCode} />
        </div>

        {/* Profile panel */}
        <div className="flex-1 bg-white shadow-sm rounded-xl flex flex-col overflow-hidden">
          {selectedMunicipality ? (
            <MunicipalityProfile />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400 gap-2">
              <div className="text-4xl">🏛️</div>
              <p className="text-sm">בחר רשות מהרשימה כדי לראות פרופיל מפורט</p>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
