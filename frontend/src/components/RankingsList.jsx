import { useState, useEffect } from 'react'
import { useDashboardStore } from '../store/dashboardStore'
import { api } from '../api/client'

const VIRIDIS = [
  '#440154', '#482777', '#3e4989', '#31688e', '#26828e',
  '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
]

function viridisByIdx(idx, total) {
  const pct = total > 1 ? 1 - idx / (total - 1) : 1
  return VIRIDIS[Math.min(9, Math.floor(pct * 10))]
}

function fmtValue(value, unit) {
  if (value == null) return '—'
  const n = Number(value)
  if (unit === '%') return n.toLocaleString('he-IL', { maximumFractionDigits: 1 }) + '%'
  if (n >= 1000) return Math.round(n).toLocaleString('he-IL')
  return n.toLocaleString('he-IL', { maximumFractionDigits: 1 })
}

export function RankingsList({ mapIndicatorCode }) {
  const { selectedYear, filterDistrict, filterType, hideRegional, setMunicipality } = useDashboardStore()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (!mapIndicatorCode) return
    setLoading(true)
    api.getAllRankings(mapIndicatorCode, selectedYear, filterDistrict, filterType)
      .then(res => {
        let items = res.rankings
        if (hideRegional) items = items.filter(r => r.municipality_type !== 'מועצה אזורית')
        items = items.map((item, i) => ({ ...item, rank: i + 1 }))
        setData({ ...res, rankings: items })
      })
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [mapIndicatorCode, selectedYear, filterDistrict, filterType, hideRegional])

  const handleSelect = async (item) => {
    try {
      const muni = await api.getMunicipality(item.municipality_id)
      setMunicipality(muni)
    } catch {
      setMunicipality({
        id: item.municipality_id,
        name: item.name,
        district: item.district,
        municipality_type: item.municipality_type,
      })
    }
  }

  const filtered = search.trim()
    ? data?.rankings.filter(r => r.name.includes(search.trim()))
    : data?.rankings

  return (
    <div className="flex flex-col h-full bg-white" dir="rtl">

      {/* Header */}
      <div className="px-4 pt-3.5 pb-3 border-b border-slate-100 flex-shrink-0">
        <h2 className="text-sm font-bold text-slate-800 leading-tight">
          {data?.indicator?.name_he || 'דירוג רשויות'}
        </h2>
        <p className="text-[10px] text-slate-400 mt-0.5">
          {filtered ? `${filtered.length} רשויות` : ''}
        </p>
      </div>

      {/* Search */}
      <div className="px-3 py-2 border-b border-slate-100 flex-shrink-0">
        <div className="relative">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="חיפוש רשות..."
            className="w-full text-xs border border-slate-200 rounded-lg px-3 py-1.5 pr-7 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 bg-slate-50 placeholder:text-slate-300 transition-all"
            dir="rtl"
          />
          <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-300 text-sm">🔍</span>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex flex-col items-center justify-center py-16 gap-2">
            <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
            <span className="text-xs text-slate-400">טוען דירוג...</span>
          </div>
        )}
        {!loading && !data && (
          <div className="flex flex-col items-center justify-center py-16 gap-2 text-slate-400">
            <span className="text-2xl">📊</span>
            <span className="text-xs">אין נתונים</span>
          </div>
        )}
        {!loading && filtered?.map((item, idx) => (
          <div
            key={item.municipality_id}
            onClick={() => handleSelect(item)}
            className="group flex items-center gap-2.5 px-4 py-2.5 border-b border-slate-50 hover:bg-blue-50/60 cursor-pointer transition-colors"
          >
            {/* Rank badge */}
            <span className="text-[11px] font-semibold text-slate-300 w-6 flex-shrink-0 text-center tabular-nums">
              {item.rank}
            </span>

            {/* Viridis dot */}
            <div
              className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm"
              style={{ background: viridisByIdx(idx, filtered.length) }}
            />

            {/* Name */}
            <span className="flex-1 text-xs font-medium text-slate-700 truncate group-hover:text-blue-700 transition-colors">
              {item.name}
            </span>

            {/* Value */}
            <span className="text-xs font-semibold text-slate-500 flex-shrink-0 tabular-nums">
              {fmtValue(item.value, data?.indicator?.unit)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
