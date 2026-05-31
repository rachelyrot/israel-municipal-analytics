import { useState, useEffect } from 'react'
import { useDashboardStore } from '../store/dashboardStore'
import { api } from '../api/client'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
} from 'recharts'

const VIRIDIS = [
  '#440154', '#482777', '#3e4989', '#31688e', '#26828e',
  '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
]

function clusterColor(cluster) {
  if (!cluster) return '#6baed6'
  return VIRIDIS[Math.min(9, Math.max(0, cluster - 1))]
}

function fmtValue(value, isPercentage, unit) {
  if (value == null) return '—'
  const n = Number(value)
  if (isPercentage) return n.toLocaleString('he-IL', { maximumFractionDigits: 1 }) + '%'
  if (unit && (unit.includes('₪') || unit.includes('שקל')))
    return '₪' + Math.round(n).toLocaleString('he-IL')
  if (n >= 10000) return Math.round(n).toLocaleString('he-IL')
  return n.toLocaleString('he-IL', { maximumFractionDigits: 1 })
}

function SectionHeader({ children }) {
  return (
    <div className="px-4 pt-4 pb-1.5">
      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{children}</span>
    </div>
  )
}

// ── Horizontal percentage bar ──────────────────────────────────────────────
function PctBar({ name, value, nationalAvg, higherIsBetter }) {
  const v = Math.min(100, Math.max(0, value ?? 0))
  const avg = nationalAvg != null ? Math.min(100, Math.max(0, nationalAvg)) : null
  const isAbove = avg != null && value > avg
  const color = avg == null ? '#3b82f6'
    : higherIsBetter === false
      ? (isAbove ? '#ef4444' : '#22c55e')
      : (isAbove ? '#22c55e' : '#ef4444')

  return (
    <div className="flex items-center gap-2.5 px-4 py-2">
      <span className="text-[11px] text-slate-500 w-24 text-right truncate flex-shrink-0 leading-tight">{name}</span>
      <div className="flex-1 flex items-center gap-2">
        <div className="relative h-1.5 bg-slate-100 rounded-full flex-1">
          <div
            className="absolute top-0 right-0 h-full rounded-full transition-all duration-500"
            style={{ width: `${v}%`, background: color }}
          />
          {avg != null && (
            <div
              className="absolute top-[-4px] h-[14px] w-[2px] rounded-full"
              style={{ right: `${avg}%`, background: '#94a3b8' }}
            />
          )}
        </div>
        <span className="text-[11px] font-semibold text-slate-600 w-9 flex-shrink-0 text-left tabular-nums">
          {v.toLocaleString('he-IL', { maximumFractionDigits: 1 })}%
        </span>
      </div>
    </div>
  )
}

// ── Land-use donut ─────────────────────────────────────────────────────────
const LAND_CODES = [
  { code: 'LAND_RESIDENTIAL_PCT', label: 'מגורים',    color: '#3b82f6' },
  { code: 'LAND_COMMERCIAL_PCT',  label: 'תעשייה',    color: '#f59e0b' },
  { code: 'LAND_OPEN_PCT',        label: 'שטח פתוח',  color: '#22c55e' },
]

function LandUseDonut({ kpis }) {
  const data = LAND_CODES
    .map(({ code, label, color }) => {
      const kpi = kpis.find(k => k.indicator_code === code)
      return kpi && kpi.value != null ? { name: label, value: kpi.value, color } : null
    })
    .filter(Boolean)

  if (data.length < 2) return null

  return (
    <>
      <SectionHeader>שימושי קרקע</SectionHeader>
      <div className="flex items-center gap-4 px-4 py-3 bg-slate-50 mx-3 rounded-xl mb-1">
        <PieChart width={88} height={88}>
          <Pie
            data={data}
            cx={40} cy={40}
            innerRadius={24} outerRadius={40}
            dataKey="value"
            strokeWidth={0}
          >
            {data.map((d, i) => <Cell key={i} fill={d.color} />)}
          </Pie>
          <Tooltip
            formatter={(v) => [v.toFixed(1) + '%', '']}
            contentStyle={{ fontSize: 11, direction: 'rtl', borderRadius: 8 }}
          />
        </PieChart>
        <div className="flex flex-col gap-2.5">
          {data.map((d, i) => (
            <div key={i} className="flex items-center gap-2 text-xs">
              <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: d.color }} />
              <span className="text-slate-500">{d.name}</span>
              <span className="font-bold text-slate-700 mr-1">{d.value.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

// ── Radar chart (ratio to national avg) ───────────────────────────────────
const RADAR_CODES = [
  'EDU_MATRIC_RATE', 'WAGE_AVG', 'EMP_UNEMP_RATE',
  'BUDGET_INCOME_PC', 'INFRA_RECYCLING', 'POP_FERTILITY_RATE',
  'HEALTH_GOOD_STATUS_PCT', 'SOCIAL_LIFE_SATISFACTION',
]

function KPIRadar({ kpis }) {
  const data = kpis
    .filter(k =>
      RADAR_CODES.includes(k.indicator_code) &&
      k.value != null && k.national_avg != null && k.national_avg > 0
    )
    .map(k => ({
      subject: k.name_he.length > 11 ? k.name_he.slice(0, 10) + '…' : k.name_he,
      value: Math.min(2, Math.max(0.05, k.value / k.national_avg)),
      fullMark: 2,
    }))

  if (data.length < 3) return null

  return (
    <>
      <SectionHeader>ביחס לממוצע הארצי</SectionHeader>
      <div className="px-3 pb-1">
        <ResponsiveContainer width="100%" height={200}>
          <RadarChart cx="50%" cy="50%" outerRadius="62%" data={data}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis
              dataKey="subject"
              tick={{ fontSize: 10, fill: '#94a3b8' }}
            />
            <Radar
              dataKey="value"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.2}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
        <p className="text-center text-[10px] text-slate-400 -mt-2 mb-1">1.0 = ממוצע ארצי</p>
      </div>
    </>
  )
}

// ── Similar municipalities ─────────────────────────────────────────────────
function SimilarMunis({ municipalityId, year }) {
  const [similar, setSimilar] = useState([])
  const { setMunicipality } = useDashboardStore()

  useEffect(() => {
    if (!municipalityId) return
    setSimilar([])
    api.getSimilar(municipalityId, year)
      .then(data => {
        const list = Array.isArray(data)
          ? data
          : (data.similar_municipalities || data.similar || [])
        setSimilar(list.slice(0, 6))
      })
      .catch(() => {})
  }, [municipalityId, year])

  if (!similar.length) return null

  const handleClick = async (s) => {
    try {
      const muni = await api.getMunicipality(s.municipality_id ?? s.id)
      setMunicipality(muni)
    } catch {}
  }

  return (
    <>
      <SectionHeader>רשויות דומות</SectionHeader>
      <div className="px-4 pb-3 flex flex-wrap gap-1.5">
        {similar.map(s => (
          <button
            key={s.municipality_id ?? s.id}
            onClick={() => handleClick(s)}
            className="px-3 py-1 bg-slate-100 text-xs text-slate-600 rounded-full hover:bg-blue-100 hover:text-blue-700 transition-colors font-medium"
          >
            {s.name}
          </button>
        ))}
      </div>
    </>
  )
}

// ── Priority codes for top 2-col grid ─────────────────────────────────────
const TOP_CODES = [
  'POP_TOTAL', 'SOCIO_CLUSTER', 'EDU_MATRIC_RATE', 'WAGE_AVG',
  'EMP_UNEMP_RATE', 'BUDGET_INCOME_PC', 'POP_FERTILITY_RATE', 'POP_AGE_65_PLUS',
]

const BAR_CODES = [
  'POP_IMMIGRANTS_PCT', 'POP_AGE_65_PLUS', 'EDU_HIGHER_EDUCATION',
  'SOCIAL_HOUSING_OWNERSHIP', 'INFRA_RECYCLING', 'EDU_MATRIC_RATE',
]

// ── Main component ─────────────────────────────────────────────────────────
export function MunicipalityProfile() {
  const { selectedMunicipality, selectedYear, kpis, isLoadingKPIs, setMunicipality } = useDashboardStore()
  if (!selectedMunicipality) return null

  const cluster = selectedMunicipality.socioeconomic_cluster
  const dotColor = clusterColor(cluster)

  const topKPIs  = TOP_CODES.map(code => kpis.find(k => k.indicator_code === code)).filter(Boolean)
  const restKPIs = kpis.filter(k => !TOP_CODES.includes(k.indicator_code))

  const barKPIs = BAR_CODES
    .map(code => kpis.find(k => k.indicator_code === code))
    .filter(k => k && k.value != null)

  return (
    <div className="flex flex-col h-full bg-white" dir="rtl">

      {/* ── Sticky header ── */}
      <div className="px-4 py-3 border-b border-slate-100 flex items-center gap-2.5 flex-shrink-0 bg-white">
        <button
          onClick={() => setMunicipality(null)}
          className="w-7 h-7 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 text-lg leading-none flex-shrink-0 transition-colors"
        >×</button>
        <div
          className="w-3 h-3 rounded-full flex-shrink-0 shadow-sm"
          style={{ background: dotColor }}
        />
        <span className="text-sm font-bold text-slate-900 truncate">{selectedMunicipality.name}</span>
      </div>

      {/* ── Tags ── */}
      <div className="px-4 py-2 border-b border-slate-100 flex gap-1.5 flex-wrap flex-shrink-0">
        {selectedMunicipality.district && (
          <span className="px-2.5 py-0.5 bg-slate-100 text-[11px] font-medium text-slate-600 rounded-full">
            מחוז {selectedMunicipality.district}
          </span>
        )}
        {selectedMunicipality.municipality_type && (
          <span className="px-2.5 py-0.5 bg-slate-100 text-[11px] font-medium text-slate-600 rounded-full">
            {selectedMunicipality.municipality_type}
          </span>
        )}
        {cluster && (
          <span
            className="px-2.5 py-0.5 text-[11px] font-semibold text-white rounded-full"
            style={{ background: dotColor }}
          >
            אשכול חב&quot;כ {cluster}
          </span>
        )}
      </div>

      {/* ── Scrollable body ── */}
      <div className="flex-1 overflow-y-auto">

        {isLoadingKPIs && (
          <div className="flex flex-col items-center justify-center py-16 gap-2">
            <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
            <span className="text-xs text-slate-400">טוען נתונים...</span>
          </div>
        )}

        {!isLoadingKPIs && topKPIs.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 gap-2 text-slate-400">
            <span className="text-2xl">📭</span>
            <span className="text-xs">אין נתונים לשנה זו</span>
          </div>
        )}

        {!isLoadingKPIs && topKPIs.length > 0 && (
          <>
            {/* 2-column KPI grid */}
            <div className="p-3">
              <div className="grid grid-cols-2 gap-2">
                {topKPIs.map((kpi) => (
                  <div
                    key={kpi.indicator_code}
                    className="bg-slate-50 rounded-xl p-3 border border-slate-100"
                  >
                    <div className="text-[9px] text-slate-400 leading-tight mb-1.5 truncate font-medium uppercase tracking-wide">
                      {kpi.name_he}
                    </div>
                    <div className="text-lg font-bold text-slate-900 leading-tight tabular-nums">
                      {fmtValue(kpi.value, kpi.is_percentage, kpi.unit)}
                    </div>
                    {kpi.rank_national && (
                      <div className="text-[9px] text-slate-400 mt-1 font-medium">
                        #{kpi.rank_national} מתוך 257
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-100 mx-4" />

            {/* Percentage bars */}
            {barKPIs.length > 0 && (
              <>
                <SectionHeader>מדדי אחוזים</SectionHeader>
                <div className="pb-2">
                  {barKPIs.map(kpi => (
                    <PctBar
                      key={kpi.indicator_code}
                      name={kpi.name_he}
                      value={kpi.value}
                      nationalAvg={kpi.national_avg}
                      higherIsBetter={kpi.higher_is_better}
                    />
                  ))}
                </div>
                <div className="h-px bg-slate-100 mx-4" />
              </>
            )}

            {/* Land use donut */}
            <LandUseDonut kpis={kpis} />

            {/* Radar */}
            <KPIRadar kpis={kpis} />

            {/* Similar municipalities */}
            <SimilarMunis municipalityId={selectedMunicipality.id} year={selectedYear} />

            {/* Full indicator list */}
            {restKPIs.length > 0 && (
              <>
                <div className="h-px bg-slate-100 mx-4 mt-2" />
                <SectionHeader>כל המדדים</SectionHeader>
                <div className="pb-4">
                  {restKPIs.map(kpi => (
                    <div
                      key={kpi.indicator_code}
                      className="flex justify-between items-baseline px-4 py-2 border-b border-slate-50 text-xs gap-2 last:border-0"
                    >
                      <span className="text-slate-500 truncate flex-1">{kpi.name_he}</span>
                      <span className="font-semibold text-slate-700 flex-shrink-0 tabular-nums">
                        {fmtValue(kpi.value, kpi.is_percentage, kpi.unit)}
                      </span>
                      {kpi.rank_national && (
                        <span className="text-slate-300 flex-shrink-0 text-[10px] font-medium">
                          #{kpi.rank_national}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
