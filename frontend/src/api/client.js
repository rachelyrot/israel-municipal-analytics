const BASE = '/api/v1'

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

  getIndicators: () =>
    get('/indicators'),

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

  getSimilar: (municipalityId, year) =>
    get(`/analytics/similar/${municipalityId}?year=${year}`),

  aiQuery: (question, municipalityId, year, sessionId = null, comparisonIds = null) =>
    fetch('/api/v1/ai/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        municipality_id: municipalityId,
        year,
        session_id: sessionId,
        comparison_municipality_ids: comparisonIds,
      }),
    }).then(async r => {
      if (!r.ok) {
        const body = await r.json().catch(() => ({}))
        const err = new Error(body.detail || `שגיאת שרת ${r.status}`)
        err.detail = body.detail
        throw err
      }
      return r.json()
    }),

  getInsights: (municipalityId, year) =>
    get(`/ai/insights/${municipalityId}?year=${year}`),

  getChoroplethGeoJSON: (indicatorCode, year) =>
    get(`/export/geojson?indicator_code=${indicatorCode}&year=${year}`),

  downloadPDF: (municipalityId, year) =>
    fetch(`/api/v1/export/pdf/${municipalityId}?year=${year}`)
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
