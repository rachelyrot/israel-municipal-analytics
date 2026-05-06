# שלב 3 — השוואה + ניתוח
## תת-שלבים מפורטים

---

### 3.1 — Analytics Services: comparison.py (Backend)

> ✅ הושלם — 2026-05-06 — endpoint GET /api/v1/analytics/compare מחזיר JSON עם 2 series + national_avg (נבדק עם תל אביב 504 + חיפה 452, POP_TOTAL 2015–2022)

**מה עושים:** שירות השוואת רשויות — אותו מדד, כמה רשויות, טווח שנים

**`backend/app/services/analytics/comparison.py`:**
```python
from sqlalchemy.orm import Session
from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage

def compare_municipalities(
    db: Session,
    municipality_ids: list[int],
    indicator_code: str,
    year_from: int,
    year_to: int,
) -> dict:
    """
    Returns:
    {
      "indicator": { code, name_he, unit },
      "municipalities": [
        { "id": 1, "name": "תל אביב-יפו", "series": [{ "year": 2015, "value": 123.4 }, ...] },
        ...
      ],
      "national_avg": [{ "year": 2015, "avg_value": 100.0 }, ...]
    }
    """
    ...
```

**API:** `GET /api/v1/analytics/compare?municipality_ids=1,2,3&indicator_code=POP_TOTAL&year_from=2010&year_to=2022`

**אימות:** `curl "localhost:8000/api/v1/analytics/compare?municipality_ids=1,2&indicator_code=POP_TOTAL&year_from=2015&year_to=2022"` → JSON עם 2 series

---

### 3.2 — Analytics Services: similarity.py (Backend)

> ✅ הושלם — 2026-05-06 — endpoint GET /api/v1/analytics/similar/504?year=2022&n=5 מחזיר 5 ערים דומות לתל אביב: חיפה (0.82), ראשון לציון (0.80), פתח תקווה (0.80), רמת גן (0.76), נתניה (0.75)

**מה עושים:** מציאת רשויות דומות לפי מרחק אוקלידי על 5 מדדי בסיס

**5 מדדי בסיס לחישוב דמיון:**
- אוכלוסייה (`POP_TOTAL`)
- שיעור תעסוקה (`EMP_RATE`)
- תקציב לנפש (`BUDGET_PER_CAPITA`)
- שיעור בגרות (`EDU_BAGRUT_RATE`)
- אשכול חברתי-כלכלי (`socioeconomic_cluster` מה-municipality)

**`backend/app/services/analytics/similarity.py`:**
```python
import numpy as np
from sqlalchemy.orm import Session

BASE_INDICATORS = ["POP_TOTAL", "EMP_RATE", "BUDGET_PER_CAPITA", "EDU_BAGRUT_RATE"]

def find_similar(db: Session, municipality_id: int, year: int, n: int = 5) -> list[dict]:
    """
    Returns list of n most similar municipalities, sorted by similarity score (0–1).
    [{ "id", "name", "similarity_score", "district", "municipality_type" }]
    """
    # שלב: בנה וקטור מדדים לרשות הנבחרת
    # שלב: בנה וקטורים לכל שאר הרשויות (בשנה הנתונה)
    # שלב: נרמל כל מדד (min-max) כדי למנוע דומינציה של אוכלוסייה
    # שלב: חשב מרחק אוקלידי
    # שלב: החזר N הקרובים ביותר (ללא הרשות עצמה)
    ...
```

**API:** `GET /api/v1/analytics/similar/{municipality_id}?year=2022&n=5`

**אימות:** `curl "localhost:8000/api/v1/analytics/similar/1?year=2022"` → 5 רשויות עם similarity_score

---

### 3.3 — Analytics Services: trends.py (Backend)

> ✅ הושלם — 2026-05-06 — endpoint GET /api/v1/analytics/trends/504?indicator_code=POP_TOTAL&year_from=2010&year_to=2022 מחזיר {"slope":51246.3979,"direction":"up","label_he":"מגמת עלייה","r_squared":0.7226,"pct_change_total":3678424.05,"data_points_count":13}

**מה עושים:** regression ליניארי על time series → כיוון + תווית עברית

**`backend/app/services/analytics/trends.py`:**
```python
import numpy as np
from sqlalchemy.orm import Session

def compute_trend(db: Session, municipality_id: int, indicator_code: str, year_from: int, year_to: int) -> dict:
    """
    Returns:
    {
      "slope": 2.3,           # שינוי ממוצע לשנה
      "direction": "up",      # "up" | "down" | "stable"
      "label_he": "מגמת עלייה",
      "r_squared": 0.91,      # איכות הfit (0–1)
      "pct_change_total": 18.5  # שינוי % בין year_from ל-year_to
    }
    """
    # שלב: שלוף data_points לטווח שנים
    # שלב: fit polyfit(years, values, 1) → slope, intercept
    # שלב: קבע direction: |slope/mean| < 0.02 → "stable"
    # שלב: חשב R²
    ...

LABELS = {
    "up": "מגמת עלייה",
    "down": "מגמת ירידה",
    "stable": "יציב",
}
```

**API:** `GET /api/v1/analytics/trends/{municipality_id}?indicator_code=POP_TOTAL&year_from=2010&year_to=2022`

**אימות:** `curl "localhost:8000/api/v1/analytics/trends/1?indicator_code=POP_TOTAL&year_from=2010&year_to=2022"` → `{ "direction": "up", "label_he": "מגמת עלייה", "slope": ... }`

---

### 3.4 — Analytics Services: rankings.py (Backend)

> ✅ הושלם — 2026-05-06 — endpoint GET /api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022&limit=10 מחזיר 249 רשויות ממוינות: ירושלים #1 (981k), תל אביב #2 (474k), חיפה #3 (290k) — דירוג Python enumerate, pagination אחרי מיון

**מה עושים:** דירוג רשויות לפי מדד + שנה, עם סינון לפי מחוז / סוג

**`backend/app/services/analytics/rankings.py`:**
```python
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

def get_rankings(
    db: Session,
    indicator_code: str,
    year: int,
    district: str | None = None,
    municipality_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Returns:
    {
      "indicator": { code, name_he, unit, higher_is_better },
      "year": 2022,
      "total": 256,
      "rankings": [
        { "rank": 1, "municipality_id", "name", "district", "municipality_type", "value" },
        ...
      ]
    }
    """
    # שלב: JOIN data_points + municipalities + indicators
    # שלב: WHERE indicator.code = indicator_code AND year = year
    # שלב: RANK() OVER (ORDER BY value DESC) — או ASC אם lower_is_better
    # שלב: FILTER אחרי rank אם district / municipality_type נבחרו
    ...
```

**API:** `GET /api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022&district=תל+אביב&limit=20&offset=0`

**אימות:** `curl "localhost:8000/api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022"` → רשימה ממוינת עם rank

---

### 3.5 — Analytics Router (Backend)

> ✅ הושלם — 2026-05-06 — כל 4 endpoints מחזירים 200 OK

**מה עושים:** router חדש שמחבר את כל שירותי ה-analytics ל-API

**`backend/app/routers/analytics.py`:**
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics import comparison, similarity, trends, rankings

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/compare")
def compare(municipality_ids: str, indicator_code: str, year_from: int = 2010, year_to: int = 2022, db: Session = Depends(get_db)):
    ids = [int(i) for i in municipality_ids.split(",")]
    return comparison.compare_municipalities(db, ids, indicator_code, year_from, year_to)

@router.get("/similar/{municipality_id}")
def similar(municipality_id: int, year: int = 2022, n: int = 5, db: Session = Depends(get_db)):
    return similarity.find_similar(db, municipality_id, year, n)

@router.get("/trends/{municipality_id}")
def trend(municipality_id: int, indicator_code: str, year_from: int = 2010, year_to: int = 2022, db: Session = Depends(get_db)):
    return trends.compute_trend(db, municipality_id, indicator_code, year_from, year_to)

@router.get("/rankings")
def rank(indicator_code: str, year: int, district: str = None, municipality_type: str = None, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    return rankings.get_rankings(db, indicator_code, year, district, municipality_type, limit, offset)
```

**עדכון `backend/app/main.py`:** הוסף `from app.routers import analytics` ו-`app.include_router(analytics.router, prefix="/api/v1")`

**אימות:** `curl localhost:8000/api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022` → 200 OK

---

### 3.6 — Navigation + React Router (Frontend)

> ✅ הושלם — 2026-05-06 — react-router-dom מותקן, 3 routes עובדים, build מצליח

**מה עושים:** הוספת ניווט בין הדפים (דשבורד / השוואה / דירוגים)

```bash
cd c:\new\frontend
npm install react-router-dom
```

**עדכון `frontend/src/App.jsx`:**
```jsx
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { DashboardPage } from './pages/DashboardPage'
import { ComparisonPage } from './pages/ComparisonPage'
import { RankingsPage } from './pages/RankingsPage'

function Navbar() {
  const base = "px-4 py-2 text-sm font-medium rounded-lg transition"
  const active = `${base} bg-blue-600 text-white`
  const inactive = `${base} text-gray-600 hover:bg-gray-100`

  return (
    <nav className="bg-white border-b px-6 py-2 flex gap-2" dir="rtl">
      <NavLink to="/" className={({ isActive }) => isActive ? active : inactive} end>דשבורד</NavLink>
      <NavLink to="/compare" className={({ isActive }) => isActive ? active : inactive}>השוואה</NavLink>
      <NavLink to="/rankings" className={({ isActive }) => isActive ? active : inactive}>דירוגים</NavLink>
    </nav>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/compare" element={<ComparisonPage />} />
        <Route path="/rankings" element={<RankingsPage />} />
      </Routes>
    </BrowserRouter>
  )
}
```

**אימות:** `/compare` מציג דף, `/rankings` מציג דף, ניווט בין הדפים עובד

---

### 3.7 — ComparisonPage.jsx + CompareChart.jsx (Frontend)

> ✅ הושלם — 2026-05-06 — ComparisonPage + CompareChart, build מצליח

**מה עושים:** דף השוואה — 2 רשויות + בחירת מדד + גרף קו + גרף Radar

**הוסף ל-`frontend/src/api/client.js`:**
```js
compare: (municipalityIds, indicatorCode, yearFrom = 2010, yearTo = 2022) =>
  get(`/analytics/compare?municipality_ids=${municipalityIds.join(',')}&indicator_code=${indicatorCode}&year_from=${yearFrom}&year_to=${yearTo}`),

getIndicators: () => get('/indicators'),
```

**`frontend/src/pages/ComparisonPage.jsx`:**
```jsx
import { useState } from 'react'
import { MunicipalitySelector } from '../components/selectors/MunicipalitySelector'
import { YearSelector } from '../components/selectors/YearSelector'
import { CompareChart } from '../components/charts/CompareChart'
import { api } from '../api/client'

export function ComparisonPage() {
  const [muni1, setMuni1] = useState(null)
  const [muni2, setMuni2] = useState(null)
  const [indicatorCode, setIndicatorCode] = useState('')
  const [indicators, setIndicators] = useState([])
  const [data, setData] = useState(null)

  // טעינת רשימת מדדים בהרצה ראשונה
  useEffect(() => { api.getIndicators().then(setIndicators) }, [])

  const handleCompare = async () => {
    if (!muni1 || !muni2 || !indicatorCode) return
    const result = await api.compare([muni1.id, muni2.id], indicatorCode)
    setData(result)
  }

  return (
    <div className="p-6 max-w-5xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">השוואת רשויות</h1>

      <div className="bg-white rounded-xl shadow p-4 flex gap-4 flex-wrap items-end mb-6">
        <div>
          <label className="text-sm text-gray-500 block mb-1">רשות ראשונה</label>
          <MunicipalitySelector value={muni1} onChange={setMuni1} />
        </div>
        <div>
          <label className="text-sm text-gray-500 block mb-1">רשות שנייה</label>
          <MunicipalitySelector value={muni2} onChange={setMuni2} />
        </div>
        <div>
          <label className="text-sm text-gray-500 block mb-1">מדד</label>
          <select value={indicatorCode} onChange={e => setIndicatorCode(e.target.value)}
                  className="border rounded-lg px-3 py-2 bg-white">
            <option value="">בחר מדד</option>
            {indicators.flatMap(domain =>
              domain.indicators.map(ind => (
                <option key={ind.code} value={ind.code}>{ind.name_he}</option>
              ))
            )}
          </select>
        </div>
        <button onClick={handleCompare}
                className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700">
          השווה
        </button>
      </div>

      {data && <CompareChart data={data} />}
    </div>
  )
}
```

**`frontend/src/components/charts/CompareChart.jsx`:**
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function CompareChart({ data }) {
  // מיזוג series לפי שנה לפורמט Recharts
  const merged = mergeByYear(data.municipalities)

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-lg font-semibold mb-4" dir="rtl">
        {data.indicator.name_he} ({data.indicator.unit})
      </h2>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={merged}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={v => v.toLocaleString('he-IL')} />
          <Tooltip formatter={v => v.toLocaleString('he-IL')} />
          <Legend />
          {data.municipalities.map((m, i) => (
            <Line key={m.id} dataKey={m.name} stroke={i === 0 ? '#2563eb' : '#16a34a'}
                  strokeWidth={2} dot={false} />
          ))}
          <Line dataKey="ממוצע ארצי" stroke="#9ca3af" strokeDasharray="5 5" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function mergeByYear(municipalities) {
  const byYear = {}
  municipalities.forEach(m => {
    m.series.forEach(({ year, value }) => {
      if (!byYear[year]) byYear[year] = { year }
      byYear[year][m.name] = value
    })
  })
  return Object.values(byYear).sort((a, b) => a.year - b.year)
}
```

**אימות:** בחר "תל אביב-יפו" + "חיפה" + "אוכלוסייה" → לחץ "השווה" → גרף 2 קווים מוצג

---

### 3.8 — RankingsPage.jsx (Frontend)

> ✅ הושלם — 2026-05-06 — RankingsPage עם טבלת דירוג + פילטרים, build מצליח

**מה עושים:** טבלת דירוג רשויות לפי מדד ושנה עם פילטרים

**הוסף ל-`frontend/src/api/client.js`:**
```js
getRankings: (indicatorCode, year, district = null, limit = 20, offset = 0) => {
  const p = new URLSearchParams({ indicator_code: indicatorCode, year, limit, offset })
  if (district) p.append('district', district)
  return get(`/analytics/rankings?${p}`)
},
```

**`frontend/src/pages/RankingsPage.jsx`:**
```jsx
import { useState, useEffect } from 'react'
import { api } from '../api/client'

const DISTRICTS = ['כל המחוזות', 'תל אביב', 'ירושלים', 'חיפה', 'מרכז', 'דרום', 'צפון', 'יהודה ושומרון']

export function RankingsPage() {
  const [indicators, setIndicators] = useState([])
  const [indicatorCode, setIndicatorCode] = useState('')
  const [year, setYear] = useState(2022)
  const [district, setDistrict] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.getIndicators().then(setIndicators) }, [])

  const load = async () => {
    if (!indicatorCode) return
    setLoading(true)
    const result = await api.getRankings(indicatorCode, year, district || null)
    setData(result)
    setLoading(false)
  }

  return (
    <div className="p-6 max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">דירוגי רשויות</h1>

      <div className="bg-white rounded-xl shadow p-4 flex gap-3 flex-wrap items-end mb-6">
        <select value={indicatorCode} onChange={e => setIndicatorCode(e.target.value)}
                className="border rounded-lg px-3 py-2 bg-white flex-1">
          <option value="">בחר מדד</option>
          {indicators.flatMap(d => d.indicators.map(ind =>
            <option key={ind.code} value={ind.code}>{ind.name_he}</option>
          ))}
        </select>
        <select value={year} onChange={e => setYear(Number(e.target.value))}
                className="border rounded-lg px-3 py-2 bg-white">
          {Array.from({ length: 25 }, (_, i) => 2023 - i).map(y =>
            <option key={y} value={y}>{y}</option>
          )}
        </select>
        <select value={district} onChange={e => setDistrict(e.target.value)}
                className="border rounded-lg px-3 py-2 bg-white">
          {DISTRICTS.map(d => <option key={d} value={d === 'כל המחוזות' ? '' : d}>{d}</option>)}
        </select>
        <button onClick={load}
                className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700">
          הצג דירוג
        </button>
      </div>

      {loading && <div className="text-center text-gray-400 py-12">טוען...</div>}

      {data && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="px-4 py-3 border-b text-sm text-gray-500">
            {data.indicator.name_he} ({data.indicator.unit}) · {year} · {data.total} רשויות
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-4 py-2 text-right">דירוג</th>
                <th className="px-4 py-2 text-right">רשות</th>
                <th className="px-4 py-2 text-right">מחוז</th>
                <th className="px-4 py-2 text-right">ערך</th>
              </tr>
            </thead>
            <tbody>
              {data.rankings.map(r => (
                <tr key={r.municipality_id} className="border-t hover:bg-blue-50">
                  <td className="px-4 py-2 text-gray-400 font-mono">#{r.rank}</td>
                  <td className="px-4 py-2 font-medium">{r.name}</td>
                  <td className="px-4 py-2 text-gray-500">{r.district}</td>
                  <td className="px-4 py-2 font-semibold">
                    {r.value.toLocaleString('he-IL')}
                    <span className="text-xs text-gray-400 mr-1">{data.indicator.unit}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
```

**אימות:** בחר "אוכלוסייה" 2022 → לחץ "הצג דירוג" → טבלה ממוינת של 20 רשויות

---

### 3.9 — SimilarMunicipalities panel (Frontend)

> ✅ הושלם — 2026-05-06 — SimilarMunicipalities panel ב-DashboardPage, build מצליח

**מה עושים:** פאנל ב-DashboardPage שמציג 5 רשויות הדומות לנבחרת

**הוסף ל-`frontend/src/api/client.js`:**
```js
getSimilar: (municipalityId, year) =>
  get(`/analytics/similar/${municipalityId}?year=${year}`),
```

**`frontend/src/components/SimilarMunicipalities.jsx`:**
```jsx
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { useDashboardStore } from '../store/dashboardStore'

export function SimilarMunicipalities() {
  const { selectedMunicipality, selectedYear, setMunicipality } = useDashboardStore()
  const [similar, setSimilar] = useState([])

  useEffect(() => {
    if (!selectedMunicipality) return
    api.getSimilar(selectedMunicipality.id, selectedYear).then(setSimilar)
  }, [selectedMunicipality, selectedYear])

  if (!selectedMunicipality || similar.length === 0) return null

  return (
    <div className="bg-white rounded-xl shadow p-4" dir="rtl">
      <h3 className="font-semibold text-gray-700 mb-3">רשויות דומות</h3>
      <div className="flex flex-col gap-2">
        {similar.map(m => (
          <button
            key={m.id}
            onClick={() => setMunicipality(m)}
            className="flex items-center justify-between text-sm px-3 py-2 rounded-lg hover:bg-blue-50 text-right transition"
          >
            <span className="font-medium text-gray-800">{m.name}</span>
            <span className="text-xs text-gray-400">
              {m.district} · {(m.similarity_score * 100).toFixed(0)}% דמיון
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
```

**עדכון `DashboardPage.jsx`:** הוסף `<SimilarMunicipalities />` בסיידבר או מתחת ל-KPIGrid

**אימות:** בחר "באר שבע" → פאנל מציג 5 ערים דומות עם % דמיון, לחיצה עוברת לרשות אחרת

---

## סיכום שלב 3

| תת-שלב | קובץ עיקרי | אימות | סטטוס |
|--------|-----------|-------|--------|
| 3.1 | `services/analytics/comparison.py` | `/analytics/compare?municipality_ids=1,2&indicator_code=POP_TOTAL` → 2 series | ✅ |
| 3.2 | `services/analytics/similarity.py` | `/analytics/similar/1?year=2022` → 5 רשויות עם similarity_score | ✅ |
| 3.3 | `services/analytics/trends.py` | `/analytics/trends/1?indicator_code=POP_TOTAL` → `{ direction, label_he }` | ✅ |
| 3.4 | `services/analytics/rankings.py` | `/analytics/rankings?indicator_code=POP_TOTAL&year=2022` → רשימה ממוינת | ✅ |
| 3.5 | `routers/analytics.py` + עדכון main.py | כל ה-endpoints מחזירים 200 | ✅ |
| 3.6 | `react-router-dom` + Navbar + routes | ניווט בין 3 דפים | ✅ |
| 3.7 | `ComparisonPage.jsx` + `CompareChart.jsx` | בחר 2 רשויות + מדד → גרף | ✅ |
| 3.8 | `RankingsPage.jsx` | בחר מדד + שנה → טבלה ממוינת | ✅ |
| 3.9 | `SimilarMunicipalities.jsx` | בחר רשות → 5 רשויות דומות מוצגות | ✅ |

**סדר ביצוע מומלץ:** 3.1 → 3.2 → 3.3 → 3.4 → 3.5 (backend רץ) → 3.6 → 3.7 → 3.8 → 3.9 (frontend)

**שלב 3 הושלם במלואו — 2026-05-06**
