import { useState, useEffect, useRef } from 'react'
import { LocalMunicipalitySelector } from '../components/selectors/LocalMunicipalitySelector'
import { CompareChart } from '../components/charts/CompareChart'
import { api } from '../api/client'

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
  taxes: 'מסים',
  construction: 'בנייה',
  transport: 'תחבורה',
  social: 'רווחה חברתית',
}

const MUNI_SLOTS = [0, 1, 2]

export function AnalyticsPage() {
  const [munis, setMunis] = useState([null, null, null])
  const [indicatorsByDomain, setIndicatorsByDomain] = useState({})
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [domainCharts, setDomainCharts] = useState([])
  const [loading, setLoading] = useState(false)
  const reqRef = useRef(0)

  useEffect(() => {
    api.getIndicators().then(data => {
      setIndicatorsByDomain(data)
      const first = Object.keys(data)[0]
      if (first) setSelectedDomain(first)
    })
  }, [])

  const setMuni = (idx, val) => setMunis(prev => prev.map((m, i) => i === idx ? val : m))

  const selectedIds = munis.filter(Boolean).map(m => m.id)
  const muniIdsKey = selectedIds.join(',')

  useEffect(() => {
    if (selectedIds.length === 0 || !selectedDomain) {
      setDomainCharts([])
      return
    }
    const indicators = indicatorsByDomain[selectedDomain]
    if (!indicators || indicators.length === 0) {
      setDomainCharts([])
      return
    }

    const reqId = ++reqRef.current
    setLoading(true)
    setDomainCharts([])

    Promise.all(
      indicators.map(ind =>
        api.compare(selectedIds, ind.code, 1999, 2024).catch(() => null)
      )
    ).then(results => {
      if (reqRef.current !== reqId) return
      setDomainCharts(
        results.filter(r => r && r.municipalities.some(m => m.series.length > 0))
      )
      setLoading(false)
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDomain, muniIdsKey])

  const domains = Object.keys(indicatorsByDomain)
  const hasMuni = munis[0] !== null

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50" dir="rtl">

      {/* ── Top bar: municipality selectors ── */}
      <div className="bg-white border-b px-6 py-3 flex flex-wrap gap-4 items-end flex-shrink-0">
        {MUNI_SLOTS.map(idx => (
          <div key={idx} className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500">
              {idx === 0 ? 'רשות ראשית' : `השוואה ${idx}`}
              {idx > 0 && munis[idx] && (
                <button
                  onClick={() => setMuni(idx, null)}
                  className="mr-1.5 text-slate-300 hover:text-red-400 font-bold"
                >×</button>
              )}
            </label>
            <LocalMunicipalitySelector
              value={munis[idx]}
              onChange={val => setMuni(idx, val)}
              placeholder={idx === 0 ? 'חפש רשות...' : 'הוסף להשוואה...'}
            />
          </div>
        ))}
      </div>

      {!hasMuni ? (
        <div className="flex-1 flex items-center justify-center text-slate-400">
          <div className="text-center">
            <div className="text-4xl mb-3">📊</div>
            <p className="text-sm">בחר רשות מקומית כדי לראות גרפים רב-שנתיים</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col flex-1 overflow-hidden">

          {/* ── Domain tabs ── */}
          <div className="bg-white border-b px-6 flex gap-1 overflow-x-auto flex-shrink-0 py-2">
            {domains.map(d => (
              <button
                key={d}
                onClick={() => setSelectedDomain(d)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                  selectedDomain === d
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {DOMAIN_HE[d] || d}
                <span className="mr-1.5 text-[10px] opacity-60">
                  {indicatorsByDomain[d]?.length}
                </span>
              </button>
            ))}
          </div>

          {/* ── Charts grid ── */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {loading && (
              <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
                טוען גרפים...
              </div>
            )}

            {!loading && domainCharts.length === 0 && (
              <div className="flex items-center justify-center h-32 text-slate-400 text-sm">
                אין נתונים לתחום זה עבור הרשות הנבחרת
              </div>
            )}

            {!loading && domainCharts.length > 0 && (
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                {domainCharts.map(data => (
                  <CompareChart key={data.indicator.code} data={data} height={240} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
