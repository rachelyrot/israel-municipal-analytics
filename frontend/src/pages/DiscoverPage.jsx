import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useDashboardStore } from '../store/dashboardStore'

const YEARS = Array.from({ length: 10 }, (_, i) => 2023 - i)

const DOMAIN_LABELS = {
  population:    'אוכלוסייה',
  employment:    'תעסוקה',
  education:     'חינוך',
  welfare:       'רווחה',
  budget:        'תקציב',
  infrastructure:'תשתיות',
  taxes:         'מסים',
  health:        'בריאות',
}

const CLUSTER_COLOR = [
  '', '#440154', '#482777', '#3e4989', '#31688e',
  '#26828e', '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725',
]

function deviationLabel(pct) {
  const abs = Math.abs(pct)
  if (abs >= 200) return 'חריג מאוד'
  if (abs >= 100) return 'גבוה מאוד'
  if (abs >= 60)  return 'חריג'
  return 'חריג'
}

function StoryCard({ story, onNavigate }) {
  const isHigh = story.deviation_pct > 0
  const absPct = Math.abs(story.deviation_pct)
  const clusterColor = CLUSTER_COLOR[story.socioeconomic_cluster] || '#6baed6'
  const domainLabel = DOMAIN_LABELS[story.domain] || story.domain

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">

      {/* Tags row */}
      <div className="flex items-center gap-2 flex-wrap">
        <span
          className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold text-white"
          style={{ background: clusterColor }}
        >
          אשכול {story.socioeconomic_cluster}
        </span>
        {story.municipality_type && (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-600">
            {story.municipality_type}
          </span>
        )}
        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-blue-50 text-blue-700">
          {domainLabel}
        </span>
      </div>

      {/* Municipality name */}
      <div>
        <h3 className="text-base font-bold text-slate-900 leading-tight">
          {story.municipality_name}
        </h3>
        {story.district && (
          <p className="text-[11px] text-slate-400 mt-0.5">{story.district}</p>
        )}
      </div>

      {/* Indicator */}
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
        {story.indicator_name_he}
      </p>

      {/* Narrative */}
      {story.narrative ? (
        <p className="text-sm text-slate-700 leading-relaxed flex-1">
          {story.narrative}
        </p>
      ) : (
        <p className="text-sm text-slate-400 italic flex-1">טוען נרטיב...</p>
      )}

      {/* Stats row */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100">
        <div className="flex items-center gap-3 text-xs">
          <span className="text-slate-500">
            ערך: <span className="font-semibold text-slate-700">
              {story.value.toLocaleString('he-IL')} {story.unit}
            </span>
          </span>
          <span className="text-slate-400">
            ממוצע: {story.national_avg.toLocaleString('he-IL')}
          </span>
        </div>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded-full ${
            isHigh
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700'
          }`}
        >
          {isHigh ? '↑' : '↓'} {absPct.toFixed(0)}%
        </span>
      </div>

      {/* Navigate button */}
      <button
        onClick={() => onNavigate(story)}
        className="text-xs text-blue-600 hover:text-blue-800 text-right font-medium transition-colors"
      >
        עבור לפרופיל ←
      </button>
    </div>
  )
}

export function DiscoverPage() {
  const [year, setYear] = useState(2020)
  const [domain, setDomain] = useState(null)
  const [stories, setStories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const { setMunicipality } = useDashboardStore()
  const navigate = useNavigate()

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    setStories([])
    api.getStories(year, 18)
      .then(data => setStories(data.stories || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [year])

  useEffect(() => { load() }, [load])

  const handleNavigate = async (story) => {
    try {
      const muni = await api.getMunicipality(story.municipality_id)
      setMunicipality(muni)
    } catch {
      setMunicipality({
        id: story.municipality_id,
        name: story.municipality_name,
        district: story.district,
        municipality_type: story.municipality_type,
        socioeconomic_cluster: story.socioeconomic_cluster,
      })
    }
    navigate('/app')
  }

  const displayed = domain
    ? stories.filter(s => s.domain === domain)
    : stories

  const domains = [...new Set(stories.map(s => s.domain))].filter(Boolean)

  return (
    <div className="min-h-screen bg-slate-100" dir="rtl">

      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-5">
        <h1 className="text-2xl font-bold text-slate-900">גילויים</h1>
        <p className="text-sm text-slate-500 mt-1">
          ממצאים מעניינים שהמערכת גילתה אוטומטית בנתוני הרשויות
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-slate-100 px-6 py-3 flex items-center gap-4 flex-wrap">
        {/* Year */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500">שנה:</span>
          <select
            value={year}
            onChange={e => setYear(Number(e.target.value))}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-100 cursor-pointer"
          >
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>

        <span className="w-px h-4 bg-slate-200" />

        {/* Domain tabs */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setDomain(null)}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              domain === null
                ? 'bg-blue-600 text-white'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            הכל
          </button>
          {domains.map(d => (
            <button
              key={d}
              onClick={() => setDomain(d)}
              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                domain === d
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {DOMAIN_LABELS[d] || d}
            </button>
          ))}
        </div>

        {/* Refresh */}
        <button
          onClick={load}
          disabled={loading}
          className="mr-auto text-xs text-slate-400 hover:text-slate-600 transition-colors disabled:opacity-40"
        >
          רענן
        </button>
      </div>

      {/* Content */}
      <div className="p-6">

        {/* Loading */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-8 h-8 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
            <p className="text-sm text-slate-400">מנתח נתונים ומייצר תובנות...</p>
            <p className="text-xs text-slate-300">(עשוי לקחת כמה שניות)</p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="max-w-md mx-auto mt-12 bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
            <p className="text-sm text-red-700 font-medium">שגיאה בטעינת הגילויים</p>
            <p className="text-xs text-red-500 mt-1">{error}</p>
            <button
              onClick={load}
              className="mt-4 px-4 py-2 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition-colors"
            >
              נסה שוב
            </button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && displayed.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 gap-3 text-slate-400">
            <span className="text-4xl">🔍</span>
            <p className="text-sm">לא נמצאו גילויים לשנה זו</p>
          </div>
        )}

        {/* Cards grid */}
        {!loading && displayed.length > 0 && (
          <>
            <p className="text-xs text-slate-400 mb-4">{displayed.length} גילויים</p>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {displayed.map((story, i) => (
                <StoryCard
                  key={`${story.municipality_id}-${story.indicator_code}`}
                  story={story}
                  onNavigate={handleNavigate}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
