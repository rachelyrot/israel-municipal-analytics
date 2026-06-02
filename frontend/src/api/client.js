const BASE = (import.meta.env.VITE_API_URL ?? '') + '/api/v1'

async function get(path) {
  const res = await fetch(BASE + path)
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

export const api = {
  searchMunicipalities: (q) =>
    get(`/municipalities/search?q=${encodeURIComponent(q)}`),

  getMunicipality: (id) =>
    get(`/municipalities/${id}`),

  getIndicators: (year = null) =>
    get(year ? `/indicators?year=${year}` : '/indicators'),

  getKPIs: (municipalityId, year, domain = null) => {
    const domainParam = domain ? `&domain=${domain}` : ''
    return get(`/data/kpis/${municipalityId}?year=${year}${domainParam}`)
  },

  getTimeSeries: (municipalityId, indicatorCode, yearFrom = 1999, yearTo = 2024) =>
    get(`/data/timeseries/${municipalityId}/single?indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`),

  compare: (municipalityIds, indicatorCode, yearFrom = 1999, yearTo = 2024) =>
    get(`/analytics/compare?municipality_ids=${municipalityIds.join(',')}&indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`),

  getRankings: (indicatorCode, year, district = null, limit = 20, offset = 0) => {
    const p = new URLSearchParams({ indicator_code: indicatorCode, year, limit, offset })
    if (district) p.append('district', district)
    return get(`/analytics/rankings?${p}`)
  },

  getAllRankings: (indicatorCode, year, district = null, type = null) => {
    const p = new URLSearchParams({ indicator_code: indicatorCode, year, limit: 300 })
    if (district) p.append('district', district)
    if (type) p.append('municipality_type', type)
    return get(`/analytics/rankings?${p}`)
  },

  getSimilar: (municipalityId, year) =>
    get(`/analytics/similar/${municipalityId}?year=${year}`),

  aiQuery: (question, municipalityId, year, sessionId = null, comparisonIds = null) => {
    const body = { question }
    if (municipalityId != null) body.municipality_id = municipalityId
    if (year != null) body.year = year
    if (sessionId != null) body.session_id = sessionId
    if (comparisonIds != null) body.comparison_municipality_ids = comparisonIds
    return fetch(BASE + '/ai/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).then(async r => {
      if (!r.ok) {
        const resp = await r.json().catch(() => ({}))
        const detail = resp.detail
        const detailStr = Array.isArray(detail)
          ? detail.map(e => e.msg || JSON.stringify(e)).join('; ')
          : (typeof detail === 'string' ? detail : null)
        const err = new Error(detailStr || `שגיאת שרת ${r.status}`)
        err.detail = detailStr
        throw err
      }
      return r.json()
    })
  },

  clearSession: (sessionId) =>
    fetch(`${BASE}/ai/session/${sessionId}`, { method: 'DELETE' }).catch(() => {}),

  getInsights: (municipalityId, year) =>
    get(`/ai/insights/${municipalityId}?year=${year}`),

  getChoroplethGeoJSON: (indicatorCode, year) =>
    get(`/export/geojson?indicator_code=${indicatorCode}&year=${year}`),

  downloadPDF: (municipalityId, year) =>
    fetch(`${BASE}/export/pdf/${municipalityId}?year=${year}`)
      .then(r => {
        if (!r.ok) throw new Error(`PDF error ${r.status}`)
        return r.blob()
      })
      .then(blob => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `report_${municipalityId}_${year}.pdf`
        a.click()
        URL.revokeObjectURL(url)
      }),

  getForecast: (municipalityId, indicatorCode, deltaPct = 0, yearsAhead = 5) =>
    get(`/analytics/forecast/${municipalityId}?indicator_code=${indicatorCode}&delta_pct=${deltaPct}&years_ahead=${yearsAhead}`),
}
