import { useState, useEffect, useRef, useMemo } from 'react'
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

const getMuniColor = (i) => `hsl(${Math.round((i * 137.508 + 220) % 360)}, 65%, 48%)`

function MuniAdder({ onAdd, excluded }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  useEffect(() => {
    if (query.length < 2) { setResults([]); setOpen(false); return }
    const t = setTimeout(() =>
      api.searchMunicipalities(query)
        .then(data => {
          const filtered = data.filter(m => !excluded.has(m.id))
          setResults(filtered)
          setOpen(filtered.length > 0)
        })
        .catch(() => {}),
      300
    )
    return () => clearTimeout(t)
  }, [query, excluded])

  useEffect(() => {
    function handleClick(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleSelect = (m) => {
    onAdd(m)
    setQuery('')
    setResults([])
    setOpen(false)
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="flex items-center border border-dashed border-slate-300 rounded-full bg-white px-3 py-1.5 shadow-sm gap-1.5 cursor-text">
        <span className="text-slate-400 text-base leading-none">+</span>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="הוסף רשות..."
          className="w-36 outline-none text-sm text-right bg-transparent placeholder-slate-400"
          dir="rtl"
        />
      </div>
      {open && (
        <div className="absolute top-full mt-1 right-0 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-56 overflow-y-auto">
          {results.map(m => (
            <div
              key={m.id}
              onClick={() => handleSelect(m)}
              className="px-4 py-2.5 hover:bg-blue-50 cursor-pointer flex justify-between items-center"
              dir="rtl"
            >
              <span className="font-medium text-sm">{m.name}</span>
              <span className="text-xs text-gray-400">{m.municipality_type} · {m.district}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function IndicatorSearch({ indicatorsByDomain, onSelect }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  const allIndicators = useMemo(() =>
    Object.entries(indicatorsByDomain).flatMap(([domain, inds]) =>
      inds.map(ind => ({ ...ind, domain }))
    ), [indicatorsByDomain])

  const results = useMemo(() => {
    if (query.length < 2) return []
    const q = query.toLowerCase()
    return allIndicators.filter(ind => ind.name_he.toLowerCase().includes(q)).slice(0, 12)
  }, [query, allIndicators])

  useEffect(() => {
    setOpen(results.length > 0)
  }, [results])

  useEffect(() => {
    function handleClick(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleSelect = (ind) => {
    onSelect(ind)
    setQuery('')
    setOpen(false)
  }

  return (
    <div ref={containerRef} className="relative flex-shrink-0">
      <div className="flex items-center border border-slate-200 rounded-lg bg-slate-50 px-3 py-1.5 gap-2 w-52">
        <span className="text-slate-400 text-sm">🔍</span>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="חפש מדד..."
          className="flex-1 outline-none text-sm text-right bg-transparent placeholder-slate-400"
          dir="rtl"
        />
        {query && (
          <button onClick={() => { setQuery(''); setOpen(false) }} className="text-slate-300 hover:text-slate-500 leading-none">×</button>
        )}
      </div>
      {open && (
        <div className="absolute top-full mt-1 left-0 w-72 bg-white border border-gray-200 rounded-lg shadow-xl z-50 max-h-72 overflow-y-auto">
          {results.map(ind => (
            <div
              key={ind.code}
              onClick={() => handleSelect(ind)}
              className="px-4 py-2.5 hover:bg-blue-50 cursor-pointer flex justify-between items-center gap-3"
              dir="rtl"
            >
              <span className="font-medium text-sm">{ind.name_he}</span>
              <span className="text-xs text-slate-400 whitespace-nowrap shrink-0 bg-slate-100 px-2 py-0.5 rounded-full">
                {DOMAIN_HE[ind.domain] || ind.domain}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function AnalyticsPage() {
  const [munis, setMunis] = useState([])
  const [indicatorsByDomain, setIndicatorsByDomain] = useState({})
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [domainCharts, setDomainCharts] = useState([])
  const [loading, setLoading] = useState(false)
  const [highlightedCode, setHighlightedCode] = useState(null)
  const reqRef = useRef(0)

  useEffect(() => {
    api.getIndicators().then(data => {
      setIndicatorsByDomain(data)
      const first = Object.keys(data)[0]
      if (first) setSelectedDomain(first)
    })
  }, [])

  const addMuni = (muni) => {
    setMunis(prev => {
      if (prev.find(m => m.id === muni.id)) return prev
      return [...prev, muni]
    })
  }

  const removeMuni = (id) => setMunis(prev => prev.filter(m => m.id !== id))

  const handleIndicatorSelect = (ind) => {
    setSelectedDomain(ind.domain)
    setHighlightedCode(ind.code)
  }

  // Scroll to highlighted chart once it's rendered
  useEffect(() => {
    if (!highlightedCode || loading) return
    const el = document.getElementById(`chart-${highlightedCode}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      const timer = setTimeout(() => setHighlightedCode(null), 2500)
      return () => clearTimeout(timer)
    }
  }, [highlightedCode, loading, domainCharts])

  const selectedIds = munis.map(m => m.id)
  const excludedIds = new Set(selectedIds)
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

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50" dir="rtl">

      {/* ── Top bar: municipality chips + adder ── */}
      <div className="bg-white border-b px-6 py-3 flex flex-wrap gap-2 items-center flex-shrink-0 min-h-[60px]">
        {munis.map((m, i) => (
          <span
            key={m.id}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium text-white select-none"
            style={{ backgroundColor: getMuniColor(i) }}
          >
            {m.name}
            <button
              onClick={() => removeMuni(m.id)}
              className="opacity-70 hover:opacity-100 leading-none font-bold"
              aria-label={`הסר ${m.name}`}
            >×</button>
          </span>
        ))}
        <MuniAdder onAdd={addMuni} excluded={excludedIds} />
        {munis.length > 1 && (
          <span className="text-xs text-slate-400 mr-2">
            {munis.length} רשויות · כולל ממוצע ארצי
          </span>
        )}
      </div>

      {munis.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-slate-400">
          <div className="text-center">
            <div className="text-4xl mb-3">📊</div>
            <p className="text-sm">חפש רשות מקומית כדי לראות גרפים רב-שנתיים</p>
            <p className="text-xs text-slate-300 mt-1">ניתן להוסיף כמה רשויות שרוצים להשוואה</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col flex-1 overflow-hidden">

          {/* ── Domain tabs + indicator search ── */}
          <div className="bg-white border-b px-6 flex items-center gap-3 flex-shrink-0 py-2">
            <div className="flex gap-1 overflow-x-auto flex-1">
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
            <IndicatorSearch
              indicatorsByDomain={indicatorsByDomain}
              onSelect={handleIndicatorSelect}
            />
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
                  <CompareChart
                    key={data.indicator.code}
                    data={data}
                    height={240}
                    highlighted={data.indicator.code === highlightedCode}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
