# שלב 2 — דשבורד בסיסי
## תת-שלבים מפורטים

---

### 2.1 — יצירת פרויקט Frontend (Vite + React + JavaScript + Tailwind)
> ✅ הושלם — 2026-05-05 — Vite 8 + React + Tailwind + Recharts + Zustand, build מצליח

**מה עושים:** יצירת פרויקט React חדש עם כל הכלים

```bash
cd c:\new
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install tailwindcss @tailwindcss/vite
npm install recharts
npm install zustand
```

**הגדרת Tailwind ב-`vite.config.js`:**
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { proxy: { '/api': 'http://localhost:8000' } }
})
```

**הוסף ל-`src/index.css`:**
```css
@import "tailwindcss";
```

**תוצאה:** `npm run dev` → React app רץ על `localhost:5173` ✓

---

### 2.2 — API Endpoints חדשים ב-Backend
> ✅ הושלם — 2026-05-05 — הוספת rank_national לkpis, שינוי שמות שדות, endpoint חדש timeseries/single

**מה עושים:** הוספת 2 endpoints חדשים שמחזירים נתונים מובנים לדשבורד

**`backend/app/routers/data.py`** — הוספת:

```
GET /api/v1/data/kpis/{municipality_id}?year=2022&domain=population
→ [{ indicator_code, name_he, value, national_avg, trend_pct, rank_national }]

GET /api/v1/data/timeseries/{municipality_id}?indicator_code=POP_TOTAL&year_from=2010&year_to=2022
→ [{ year, value, national_avg }]
```

**לוגיקת `kpis`:**
1. שלוף `data_points` לרשות + שנה + domain
2. לכל מדד: שלוף `national_average` לאותה שנה
3. חשב `trend_pct` — הפרש מהשנה הקודמת
4. חשב `rank_national` — SELECT RANK() OVER (ORDER BY value DESC)

**`backend/app/schemas/data.py`** — הוסף:
```python
class KPIResponse(BaseModel):
    indicator_code: str
    name_he: str
    value: float
    unit: str
    national_avg: float | None
    trend_pct: float | None   # שינוי % מהשנה הקודמת
    rank_national: int | None  # 1 = הכי גבוה בארץ

class TimeSeriesPoint(BaseModel):
    year: int
    value: float
    national_avg: float | None
```

**תוצאה:** `curl localhost:8000/api/v1/data/kpis/1?year=2022` → JSON עם מדדים ✓

---

### 2.3 — API Client (JavaScript)
> ✅ הושלם — 2026-05-05 — client.js עם כל הפונקציות

**מה עושים:** client מרכזי לכל קריאות ה-API

**`frontend/src/api/client.js`:**
```js
const BASE = '/api/v1'

export const api = {
  searchMunicipalities: (q) =>
    fetch(`${BASE}/municipalities/search?q=${q}`).then(r => r.json()),

  getMunicipality: (id) =>
    fetch(`${BASE}/municipalities/${id}`).then(r => r.json()),

  getKPIs: (municipalityId, year, domain = null) => {
    const domainParam = domain ? `&domain=${domain}` : ''
    return fetch(`${BASE}/data/kpis/${municipalityId}?year=${year}${domainParam}`).then(r => r.json())
  },

  getTimeSeries: (municipalityId, indicatorCode, yearFrom = 2010, yearTo = 2022) =>
    fetch(`${BASE}/data/timeseries/${municipalityId}?indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`).then(r => r.json()),

  getIndicators: () =>
    fetch(`${BASE}/indicators`).then(r => r.json()),
}
```

**תוצאה:** `api.getKPIs(1, 2022)` מחזיר נתונים תקינים בקונסול ✓

---

### 2.4 — Zustand Store (dashboardStore.js)
> ✅ הושלם — 2026-05-05 — dashboardStore עם fetchKPIs אוטומטי + טיפול בשגיאות

**מה עושים:** state מרכזי לכל הדשבורד

**`frontend/src/store/dashboardStore.js`:**
```js
import { create } from 'zustand'
import { api } from '../api/client'

export const useDashboardStore = create((set, get) => ({
  selectedMunicipality: null,
  selectedYear: 2022,
  selectedDomain: null,
  kpis: [],
  isLoadingKPIs: false,

  setMunicipality: (municipality) => {
    set({ selectedMunicipality: municipality })
    get().fetchKPIs()
  },

  setYear: (year) => {
    set({ selectedYear: year })
    get().fetchKPIs()
  },

  setDomain: (domain) => {
    set({ selectedDomain: domain })
    get().fetchKPIs()
  },

  fetchKPIs: async () => {
    const { selectedMunicipality, selectedYear, selectedDomain } = get()
    if (!selectedMunicipality) return
    set({ isLoadingKPIs: true })
    const kpis = await api.getKPIs(selectedMunicipality.id, selectedYear, selectedDomain)
    set({ kpis, isLoadingKPIs: false })
  },
}))
```

**תוצאה:** שינוי רשות בStore מפעיל טעינה אוטומטית ✓

---

### 2.5 — MunicipalitySelector.jsx
> ✅ הושלם — 2026-05-05 — debounce 300ms, dropdown, click-outside סגירה

**מה עושים:** שדה חיפוש עם Autocomplete שמחפש רשויות מה-API

**התנהגות:**
- הקלדה ≥ 2 תווים → debounce 300ms → `api.searchMunicipalities(q)`
- הצגת רשימת תוצאות (dropdown)
- בחירה → `setMunicipality(m)` בStore
- ניקוי — כפתור X

**`frontend/src/components/selectors/MunicipalitySelector.jsx`:**
```jsx
import { useState, useEffect, useRef } from 'react'
import { api } from '../../api/client'
import { useDashboardStore } from '../../store/dashboardStore'

export function MunicipalitySelector() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const { selectedMunicipality, setMunicipality } = useDashboardStore()

  useEffect(() => {
    if (query.length < 2) { setResults([]); return }
    const t = setTimeout(() =>
      api.searchMunicipalities(query).then(data => { setResults(data); setOpen(true) }),
      300
    )
    return () => clearTimeout(t)
  }, [query])

  const handleSelect = (m) => {
    setMunicipality(m)
    setQuery(m.name)
    setOpen(false)
  }

  const handleClear = () => {
    setMunicipality(null)
    setQuery('')
    setResults([])
  }

  return (
    <div className="relative w-64">
      <div className="flex items-center border rounded-lg bg-white px-3">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="חפש רשות מקומית..."
          className="flex-1 py-2 outline-none text-right"
          dir="rtl"
        />
        {query && <button onClick={handleClear} className="text-gray-400 hover:text-gray-600">✕</button>}
      </div>
      {open && results.length > 0 && (
        <div className="absolute top-full mt-1 w-full bg-white border rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
          {results.map(m => (
            <div key={m.id} onClick={() => handleSelect(m)}
                 className="px-4 py-2 hover:bg-blue-50 cursor-pointer text-right" dir="rtl">
              {m.name}
              <span className="text-xs text-gray-400 mr-2">{m.municipality_type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

**תוצאה:** חיפוש "תל" → רשימה מוצגת, בחירה → השם מוצג בשדה ✓

---

### 2.6 — YearSelector.jsx
> ✅ הושלם — 2026-05-05 — dropdown 1999–2023

**מה עושים:** Dropdown לבחירת שנה (1999–2023)

**`frontend/src/components/selectors/YearSelector.jsx`:**
```jsx
import { useDashboardStore } from '../../store/dashboardStore'

export function YearSelector() {
  const { selectedYear, setYear } = useDashboardStore()
  const years = Array.from({ length: 25 }, (_, i) => 2023 - i)

  return (
    <select
      value={selectedYear}
      onChange={e => setYear(Number(e.target.value))}
      className="border rounded-lg px-3 py-2 bg-white"
      dir="rtl"
    >
      {years.map(y => <option key={y} value={y}>{y}</option>)}
    </select>
  )
}
```

**תוצאה:** שינוי שנה → Store מתעדכן → KPIs נטענים מחדש ✓

---

### 2.7 — KPICard.jsx + KPIGrid.jsx
> ✅ הושלם — 2026-05-05 — כרטיסים עם ערך, מגמה, vs ארצי, דירוג + skeleton loading

**מה עושים:** כרטיסי מדד עם ערך, מגמה, והשוואה לממוצע ארצי

**`frontend/src/components/kpi/KPICard.jsx`:**
```jsx
export function KPICard({ kpi, onSelect, selected }) {
  const trendUp = kpi.trend_pct > 0
  const trendColor = trendUp ? 'text-green-600' : 'text-red-600'
  const vsNational = kpi.national_avg
    ? ((kpi.value - kpi.national_avg) / kpi.national_avg * 100).toFixed(1)
    : null

  return (
    <div
      onClick={() => onSelect(kpi.indicator_code)}
      className={`bg-white rounded-xl shadow p-4 flex flex-col gap-1 cursor-pointer transition
        ${selected ? 'ring-2 ring-blue-500' : 'hover:shadow-md'}`}
      dir="rtl"
    >
      <span className="text-xs text-gray-500">{kpi.name_he}</span>
      <span className="text-2xl font-bold">
        {kpi.value.toLocaleString('he-IL')}
        <span className="text-sm font-normal text-gray-500 mr-1">{kpi.unit}</span>
      </span>
      {kpi.trend_pct != null && (
        <span className={`text-sm ${trendColor}`}>
          {trendUp ? '↑' : '↓'} {Math.abs(kpi.trend_pct).toFixed(1)}% משנה קודמת
        </span>
      )}
      {vsNational && (
        <span className="text-xs text-gray-400">
          {Number(vsNational) > 0 ? '+' : ''}{vsNational}% מהממוצע הארצי
        </span>
      )}
      {kpi.rank_national && (
        <span className="text-xs text-gray-400">דירוג ארצי: #{kpi.rank_national}</span>
      )}
    </div>
  )
}
```

**`frontend/src/components/kpi/KPIGrid.jsx`:**
```jsx
import { useDashboardStore } from '../../store/dashboardStore'
import { KPICard } from './KPICard'

export function KPIGrid({ selectedIndicator, onSelectIndicator }) {
  const { kpis, isLoadingKPIs } = useDashboardStore()

  if (isLoadingKPIs) return (
    <div className="flex justify-center py-12 text-gray-400">טוען נתונים...</div>
  )

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {kpis.map(kpi => (
        <KPICard
          key={kpi.indicator_code}
          kpi={kpi}
          selected={selectedIndicator === kpi.indicator_code}
          onSelect={onSelectIndicator}
        />
      ))}
    </div>
  )
}
```

**תוצאה:** בחירת רשות → Grid של כרטיסים מוצג עם כל הנתונים ✓

---

### 2.8 — TimeSeriesChart.jsx
> ✅ הושלם — 2026-05-05 — Recharts עם 2 קווים, Tooltip עברי, loading state

**מה עושים:** גרף קו רב-שנתי עם Recharts — ערך הרשות + ממוצע ארצי

**`frontend/src/components/charts/TimeSeriesChart.jsx`:**
```jsx
import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { api } from '../../api/client'
import { useDashboardStore } from '../../store/dashboardStore'

export function TimeSeriesChart({ indicatorCode, municipalityName }) {
  const { selectedMunicipality } = useDashboardStore()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selectedMunicipality || !indicatorCode) return
    setLoading(true)
    api.getTimeSeries(selectedMunicipality.id, indicatorCode)
      .then(setData)
      .finally(() => setLoading(false))
  }, [selectedMunicipality, indicatorCode])

  if (loading) return <div className="text-center py-8 text-gray-400">טוען גרף...</div>

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="year" />
        <YAxis tickFormatter={v => v.toLocaleString('he-IL')} />
        <Tooltip formatter={v => v.toLocaleString('he-IL')} />
        <Legend />
        <Line dataKey="value" name={municipalityName} stroke="#2563eb" strokeWidth={2} dot={false} />
        <Line dataKey="national_avg" name="ממוצע ארצי" stroke="#9ca3af"
              strokeDasharray="5 5" strokeWidth={1.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

**תוצאה:** לחיצה על כרטיס → גרף מוצג עם 2 קווים ✓

---

### 2.9 — DomainFilter.jsx
> ✅ הושלם — 2026-05-05 — 8 תחומים כפתורי pill

**מה עושים:** כפתורי סינון לפי תחום

**`frontend/src/components/DomainFilter.jsx`:**
```jsx
import { useDashboardStore } from '../store/dashboardStore'

const DOMAINS = [
  { key: null, label: 'הכל' },
  { key: 'population', label: 'אוכלוסייה' },
  { key: 'education', label: 'חינוך' },
  { key: 'employment', label: 'תעסוקה' },
  { key: 'budget', label: 'תקציב' },
  { key: 'welfare', label: 'רווחה' },
]

export function DomainFilter() {
  const { selectedDomain, setDomain } = useDashboardStore()

  return (
    <div className="flex gap-2 flex-wrap" dir="rtl">
      {DOMAINS.map(d => (
        <button
          key={d.key ?? 'all'}
          onClick={() => setDomain(d.key)}
          className={`px-4 py-1.5 rounded-full text-sm transition
            ${selectedDomain === d.key
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
        >
          {d.label}
        </button>
      ))}
    </div>
  )
}
```

**תוצאה:** לחיצה על "חינוך" → KPIGrid מציג רק מדדי חינוך ✓

---

### 2.10 — DashboardPage.jsx (הרכבה סופית)
> ✅ הושלם — 2026-05-05 — DashboardPage מלא, App.jsx מעודכן, build מצליח (551KB)

**מה עושים:** הרכבת כל הקומפוננטות לדף אחד קוהרנטי

**`frontend/src/pages/DashboardPage.jsx`:**
```jsx
import { useState } from 'react'
import { useDashboardStore } from '../store/dashboardStore'
import { MunicipalitySelector } from '../components/selectors/MunicipalitySelector'
import { YearSelector } from '../components/selectors/YearSelector'
import { DomainFilter } from '../components/DomainFilter'
import { KPIGrid } from '../components/kpi/KPIGrid'
import { TimeSeriesChart } from '../components/charts/TimeSeriesChart'

export function DashboardPage() {
  const { selectedMunicipality, selectedYear } = useDashboardStore()
  const [selectedIndicator, setSelectedIndicator] = useState(null)

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <header className="bg-white shadow px-6 py-4 flex gap-4 items-center flex-wrap">
        <h1 className="text-xl font-bold text-gray-800 ml-auto">ניתוח רשויות מקומיות</h1>
        <MunicipalitySelector />
        <YearSelector />
      </header>

      <main className="p-6 flex flex-col gap-6 max-w-7xl mx-auto">
        {!selectedMunicipality && (
          <div className="text-center text-gray-400 mt-32 text-lg">
            בחר רשות מקומית להתחיל
          </div>
        )}

        {selectedMunicipality && <>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{selectedMunicipality.name}</h2>
            <p className="text-gray-500">
              {selectedMunicipality.municipality_type} · {selectedMunicipality.district} · שנת {selectedYear}
            </p>
          </div>

          <DomainFilter />

          <KPIGrid
            selectedIndicator={selectedIndicator}
            onSelectIndicator={setSelectedIndicator}
          />

          {selectedIndicator && (
            <div className="bg-white rounded-xl shadow p-6">
              <TimeSeriesChart
                indicatorCode={selectedIndicator}
                municipalityName={selectedMunicipality.name}
              />
            </div>
          )}
        </>}
      </main>
    </div>
  )
}
```

**עדכון `frontend/src/App.jsx`:**
```jsx
import { DashboardPage } from './pages/DashboardPage'

export default function App() {
  return <DashboardPage />
}
```

**תוצאה:** `npm run dev` → דף מלא עם כל הפיצ'רים ✓

---

## סיכום שלב 2

| תת-שלב | קובץ | אימות |
|--------|------|-------|
| 2.1 | `npm create vite` (react) + Tailwind + Recharts | `npm run dev` → localhost:5173 |
| 2.2 | `/data/kpis` + `/data/timeseries` endpoints (Python) | `curl localhost:8000/api/v1/data/kpis/1?year=2022` |
| 2.3 | `api/client.js` | קריאה מהקונסול מחזירה נתונים |
| 2.4 | `dashboardStore.js` (Zustand) | שינוי רשות → fetch אוטומטי |
| 2.5 | `MunicipalitySelector.jsx` | חיפוש "תל" → dropdown |
| 2.6 | `YearSelector.jsx` | שינוי שנה → KPIs מתרעננים |
| 2.7 | `KPICard.jsx` + `KPIGrid.jsx` | Grid עם ערכים, מגמות, דירוגים |
| 2.8 | `TimeSeriesChart.jsx` | גרף 2 קווים (רשות + ארצי) |
| 2.9 | `DomainFilter.jsx` | סינון לפי תחום |
| 2.10 | `DashboardPage.jsx` | בחר "תל אביב-יפו" 2022 → הכל מוצג |
