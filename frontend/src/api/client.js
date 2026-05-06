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

  getTimeSeries: (municipalityId, indicatorCode, yearFrom = 2005, yearTo = 2023) =>
    get(`/data/timeseries/${municipalityId}/single?indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`),

  compare: (municipalityIds, indicatorCode, yearFrom = 2010, yearTo = 2023) =>
    get(`/analytics/compare?municipality_ids=${municipalityIds.join(',')}&indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`),

  getRankings: (indicatorCode, year, district = null, limit = 20, offset = 0) => {
    const p = new URLSearchParams({ indicator_code: indicatorCode, year, limit, offset })
    if (district) p.append('district', district)
    return get(`/analytics/rankings?${p}`)
  },
}
