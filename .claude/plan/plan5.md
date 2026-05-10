# שלב 5 — מפות + PDF + תחזיות
## תת-שלבים מפורטים

---

### 5.1 — GeoJSON + geojson_builder.py (Backend)

> ✅ הושלם — 2026-05-10 — geojson_builder.py (Point-based), routers/export.py, scripts/seed_coordinates.py נוצרו. Import תקין. לפני שימוש יש להריץ: `python scripts/seed_coordinates.py` כדי לאכלס lat/lon ב-DB.

**מה עושים:** שירות שמחבר DataPoints ל-GeoJSON גאוגרפי לפי `symbol_cbs`, מוכן לצביעה כורופלת

**הכנת קובץ GeoJSON:**
```
frontend/public/israel_municipalities.geojson
```
הורד מ: https://data.gov.il/dataset/municipal-boundaries  
מבנה נדרש — כל Feature צריך שדה `muni_code` (= CBS symbol) ב-properties.

**התקנה:**
```bash
pip install shapely
```
הוסף ל-`backend/requirements.txt`:
```
shapely==2.1.0
```

**`backend/app/services/export/geojson_builder.py`:**
```python
import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality

GEOJSON_PATH = Path(__file__).resolve().parents[4] / "frontend" / "public" / "israel_municipalities.geojson"


def build_choropleth_geojson(db: Session, indicator_code: str, year: int) -> dict:
    """
    טוען את ה-GeoJSON הבסיסי ומוסיף לכל Feature את הערך של המדד הנבחר.
    מחזיר GeoJSON FeatureCollection עם properties.value + properties.municipality_name.
    """
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(f"GeoJSON not found at {GEOJSON_PATH}")

    with open(GEOJSON_PATH, encoding="utf-8") as f:
        geojson = json.load(f)

    # שלוף כל DataPoints למדד + שנה
    rows = (
        db.query(DataPoint, Municipality)
        .join(Municipality, DataPoint.municipality_id == Municipality.id)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(
            and_(
                Indicator.code == indicator_code,
                DataPoint.year == year,
                DataPoint.value.isnot(None),
            )
        )
        .all()
    )

    # בנה מפת symbol_cbs → ערך
    symbol_to_value: dict[str, float] = {
        str(int(muni.symbol_cbs)): dp.value
        for dp, muni in rows
        if muni.symbol_cbs
    }

    # הוסף value לכל Feature
    for feature in geojson.get("features", []):
        props = feature.setdefault("properties", {})
        symbol = str(props.get("muni_code", "")).strip()
        props["value"] = symbol_to_value.get(symbol)
        props["has_data"] = symbol in symbol_to_value

    return geojson
```

**`backend/app/services/export/__init__.py`** — ריק

**`backend/app/routers/export.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export import geojson_builder

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/geojson")
def choropleth_geojson(indicator_code: str, year: int = 2022, db: Session = Depends(get_db)):
    """
    GeoJSON כורופלט לפי מדד ושנה.
    GET /api/v1/export/geojson?indicator_code=POP_TOTAL&year=2022
    """
    try:
        return JSONResponse(content=geojson_builder.build_choropleth_geojson(db, indicator_code, year))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
```

**עדכון `backend/app/main.py`:**
```python
from app.routers import municipalities, indicators, data, admin, analytics, ai, export
app.include_router(export.router, prefix="/api/v1")
```

**אימות:**
```bash
curl "localhost:8000/api/v1/export/geojson?indicator_code=POP_TOTAL&year=2022" | python -m json.tool | head -40
# → FeatureCollection עם value בכל Feature
```

---

### 5.2 — ChoroplethMap.jsx + MapPage (Frontend)

> ✅ הושלם — 2026-05-10 — ChoroplethMap.jsx (circle markers + quantile colors + tooltip), MapPage.jsx (toolbar + legend + side panel), npm build עבר (605 modules).

**מה עושים:** מפת ישראל אינטראקטיבית, כל רשות צבועה לפי ערך המדד (5 דליים קוונטיל)

**התקנה:**
```bash
cd c:\new\frontend
npm install react-leaflet leaflet
```

**`frontend/src/pages/MapPage.jsx`:**
```jsx
import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { ChoroplethMap } from '../components/maps/ChoroplethMap'

export function MapPage() {
  const [indicators, setIndicators] = useState([])
  const [indicatorCode, setIndicatorCode] = useState('POP_TOTAL')
  const [year, setYear] = useState(2022)
  const [geojson, setGeojson] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getIndicators().then(setIndicators)
  }, [])

  useEffect(() => {
    if (!indicatorCode) return
    setLoading(true)
    api.getChoroplethGeoJSON(indicatorCode, year)
      .then(setGeojson)
      .finally(() => setLoading(false))
  }, [indicatorCode, year])

  return (
    <div className="flex flex-col h-screen" dir="rtl">
      <div className="bg-white border-b px-6 py-3 flex gap-4 items-center">
        <h1 className="text-xl font-bold">מפת רשויות</h1>
        <select
          value={indicatorCode}
          onChange={e => setIndicatorCode(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          {indicators.flatMap(d =>
            d.indicators.map(ind => (
              <option key={ind.code} value={ind.code}>{ind.name_he}</option>
            ))
          )}
        </select>
        <select
          value={year}
          onChange={e => setYear(Number(e.target.value))}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          {Array.from({ length: 25 }, (_, i) => 2023 - i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        {loading && <span className="text-sm text-gray-400">טוען...</span>}
      </div>
      <div className="flex-1">
        {geojson && <ChoroplethMap geojson={geojson} />}
      </div>
    </div>
  )
}
```

**`frontend/src/components/maps/ChoroplethMap.jsx`:**
```jsx
import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const COLORS = ['#eff3ff', '#bdd7e7', '#6baed6', '#2171b5', '#084594']

function getQuantileBreaks(values, n = 5) {
  const sorted = [...values].sort((a, b) => a - b)
  return Array.from({ length: n - 1 }, (_, i) =>
    sorted[Math.floor((sorted.length * (i + 1)) / n)]
  )
}

function getColor(value, breaks) {
  if (value == null) return '#e5e7eb'
  for (let i = 0; i < breaks.length; i++) {
    if (value <= breaks[i]) return COLORS[i]
  }
  return COLORS[COLORS.length - 1]
}

export function ChoroplethMap({ geojson }) {
  const mapRef = useRef(null)
  const layerRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    mapRef.current = L.map(containerRef.current).setView([31.5, 35.0], 8)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
    }).addTo(mapRef.current)
  }, [])

  useEffect(() => {
    if (!mapRef.current || !geojson) return
    if (layerRef.current) layerRef.current.remove()

    const values = geojson.features
      .map(f => f.properties?.value)
      .filter(v => v != null)
    const breaks = getQuantileBreaks(values)

    layerRef.current = L.geoJSON(geojson, {
      style: feature => ({
        fillColor: getColor(feature.properties?.value, breaks),
        fillOpacity: 0.75,
        color: '#fff',
        weight: 0.5,
      }),
      onEachFeature: (feature, layer) => {
        const { municipality_name, value } = feature.properties || {}
        if (municipality_name) {
          layer.bindTooltip(
            `<strong>${municipality_name}</strong><br/>${value != null ? value.toLocaleString('he-IL') : 'אין נתון'}`,
            { direction: 'top' }
          )
        }
      },
    }).addTo(mapRef.current)
  }, [geojson])

  return <div ref={containerRef} style={{ height: '100%', width: '100%' }} />
}
```

**הוסף ל-`frontend/src/api/client.js`:**
```js
getChoroplethGeoJSON: (indicatorCode, year) =>
  get(`/export/geojson?indicator_code=${indicatorCode}&year=${year}`),
```

**עדכון `frontend/src/App.jsx`:**
```jsx
import { MapPage } from './pages/MapPage'
// בnavbar:
<NavLink to="/map" ...>מפה</NavLink>
// בRoutes:
<Route path="/map" element={<MapPage />} />
```

**אימות:** פתח `/map` → מפת ישראל עם צביעה לפי אוכלוסייה → hover על רשות → tooltip עם שם + ערך

---

### 5.3 — pdf_builder.py (Backend)

> ✅ הושלם — 2026-05-10 — pdf_builder.py נוצר עם ReportLab + arabic-reshaper + python-bidi. גופן DavidLibre-Regular.ttf הורד (127KB). endpoint GET /export/pdf/{id} נוסף ל-export router.

**מה עושים:** דוח PDF בעברית לרשות + שנה — טבלת KPIs + גרפי מגמה + תובנות AI

**התקנה:**
```bash
pip install reportlab arabic-reshaper python-bidi matplotlib
```
הוסף ל-`backend/requirements.txt`:
```
reportlab==4.2.5
arabic-reshaper==3.0.0
python-bidi==0.6.6
matplotlib==3.10.3
```

**הורד גופן עברי** — שמור בנתיב `backend/app/services/export/fonts/DavidLibre-Regular.ttf`  
(הורדה: https://fonts.google.com/specimen/David+Libre → "Download family")

**`backend/app/services/export/pdf_builder.py`:**
```python
import io
from pathlib import Path
from sqlalchemy.orm import Session

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage
from sqlalchemy import and_

FONT_PATH = Path(__file__).parent / "fonts" / "DavidLibre-Regular.ttf"


def _register_font():
    if "DavidLibre" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DavidLibre", str(FONT_PATH)))


def _heb(text: str) -> str:
    """עברית תקינה ב-ReportLab: reshape + bidi."""
    return get_display(arabic_reshaper.reshape(str(text)))


def _make_trend_chart(years: list[int], values: list[float], title: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.plot(years, values, color="#2563eb", linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("שנה", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf


def build_pdf(db: Session, municipality_id: int, year: int) -> bytes:
    """
    מחזיר bytes של קובץ PDF בעברית.
    כולל: כותרת, טבלת KPIs לפי תחום, גרפי מגמה ל-4 מדדי בסיס.
    """
    _register_font()

    muni = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not muni:
        raise ValueError(f"Municipality {municipality_id} not found")

    # שלוף נתונים
    rows = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(NationalAverage.indicator_id == Indicator.id, NationalAverage.year == year),
        )
        .filter(and_(DataPoint.municipality_id == municipality_id, DataPoint.year == year))
        .order_by(Indicator.domain, Indicator.name_he)
        .all()
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    heb_style = ParagraphStyle(
        "Hebrew",
        parent=styles["Normal"],
        fontName="DavidLibre",
        fontSize=10,
        leading=16,
        alignment=2,  # ימין לשמאל
    )
    title_style = ParagraphStyle(
        "HebrewTitle",
        parent=heb_style,
        fontSize=16,
        leading=24,
        spaceAfter=6,
    )
    section_style = ParagraphStyle(
        "HebrewSection",
        parent=heb_style,
        fontSize=12,
        leading=18,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor("#2563eb"),
    )

    story = []

    # כותרת
    story.append(Paragraph(_heb(f"דוח רשות מקומית — {muni.name}"), title_style))
    story.append(Paragraph(_heb(f"שנת {year} | מחוז: {muni.district or 'לא ידוע'} | אשכול: {muni.socioeconomic_cluster or 'לא ידוע'}"), heb_style))
    story.append(Spacer(1, 0.5 * cm))

    # טבלת KPIs לפי תחום
    current_domain = None
    table_data = [[_heb("ממוצע ארצי"), _heb("יחידה"), _heb("ערך"), _heb("מדד")]]

    for dp, ind, na in rows:
        if dp.value is None:
            continue
        if ind.domain != current_domain:
            if len(table_data) > 1:
                story.append(Paragraph(_heb(current_domain or "כללי"), section_style))
                story.append(_make_table(table_data))
                story.append(Spacer(1, 0.3 * cm))
            current_domain = ind.domain
            table_data = [[_heb("ממוצע ארצי"), _heb("יחידה"), _heb("ערך"), _heb("מדד")]]

        avg_str = f"{na.avg_value:,.1f}" if na and na.avg_value else "—"
        table_data.append([
            _heb(avg_str),
            _heb(ind.unit or ""),
            _heb(f"{dp.value:,.2f}"),
            _heb(ind.name_he),
        ])

    if len(table_data) > 1:
        story.append(Paragraph(_heb(current_domain or "כללי"), section_style))
        story.append(_make_table(table_data))

    # גרפי מגמה ל-4 מדדי בסיס
    story.append(Paragraph(_heb("מגמות רב-שנתיות"), section_style))
    BASE_INDICATORS = ["POP_TOTAL", "EMP_RATE", "BUDGET_PER_CAPITA", "EDU_BAGRUT_RATE"]
    for code in BASE_INDICATORS:
        ts_rows = (
            db.query(DataPoint, Indicator)
            .join(Indicator, DataPoint.indicator_id == Indicator.id)
            .filter(
                and_(
                    DataPoint.municipality_id == municipality_id,
                    Indicator.code == code,
                    DataPoint.value.isnot(None),
                )
            )
            .order_by(DataPoint.year)
            .all()
        )
        if len(ts_rows) < 2:
            continue
        years_list = [r.year for r, _ in ts_rows]
        values_list = [r.value for r, _ in ts_rows]
        ind_name = ts_rows[0][1].name_he
        chart_buf = _make_trend_chart(years_list, values_list, ind_name)
        story.append(Image(chart_buf, width=14 * cm, height=5.5 * cm))
        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return buf.getvalue()


def _make_table(data: list[list]) -> Table:
    t = Table(data, colWidths=[3.5 * cm, 2.5 * cm, 3 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "DavidLibre"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t
```

**הוסף ל-`backend/app/routers/export.py`:**
```python
from fastapi.responses import Response
from app.services.export import pdf_builder

@router.get("/pdf/{municipality_id}")
def download_pdf(municipality_id: int, year: int = 2022, db: Session = Depends(get_db)):
    """
    PDF דוח רשות.
    GET /api/v1/export/pdf/504?year=2022
    """
    try:
        pdf_bytes = pdf_builder.build_pdf(db, municipality_id, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{municipality_id}_{year}.pdf"},
    )
```

**אימות:**
```bash
curl -o report.pdf "localhost:8000/api/v1/export/pdf/504?year=2022"
# פתח report.pdf — עברית תקינה, טבלאות, גרפים
```

---

### 5.4 — כפתור ייצוא PDF (Frontend)

> ✅ הושלם — 2026-05-10 — api.downloadPDF() + handleExportPDF() + כפתור "⬇ PDF" נוספו ל-DashboardPage. Build עבר.

**מה עושים:** כפתור "ייצא PDF" ב-DashboardPage שמוריד את הדוח ישירות מהדפדפן

**הוסף ל-`frontend/src/api/client.js`:**
```js
downloadPDF: (municipalityId, year) =>
  fetch(`/api/v1/export/pdf/${municipalityId}?year=${year}`)
    .then(r => r.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${municipalityId}_${year}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    }),
```

**הוסף ב-`frontend/src/pages/DashboardPage.jsx`** — בתוך ה-header, ליד בחירת הרשות:
```jsx
import { api } from '../api/client'

// בתוך הקומפוננטה:
const [exporting, setExporting] = useState(false)

const handleExport = async () => {
  if (!selectedMunicipality) return
  setExporting(true)
  try {
    await api.downloadPDF(selectedMunicipality.id, selectedYear)
  } finally {
    setExporting(false)
  }
}

// בJSX:
<button
  onClick={handleExport}
  disabled={!selectedMunicipality || exporting}
  className="flex items-center gap-1 px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-50 disabled:opacity-40"
>
  {exporting ? 'מייצא...' : '⬇ ייצא PDF'}
</button>
```

**אימות:** בחר "תל אביב-יפו" 2022 → לחץ "ייצא PDF" → קובץ `report_504_2022.pdf` מורד → פתח — עברית תקינה

---

### 5.5 — whatif.py (Backend)

> ✅ הושלם — 2026-05-10 — whatif.py נוצר, GET /analytics/forecast/{id} נוסף ל-analytics router. Import תקין.

**מה עושים:** חיזוי עתידי — fit linear trend על נתונים היסטוריים + הזזת פרמטר (delta%) + הקרנה 5 שנים קדימה

**`backend/app/services/analytics/whatif.py`:**
```python
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator


def forecast(
    db: Session,
    municipality_id: int,
    indicator_code: str,
    delta_pct: float = 0.0,
    years_ahead: int = 5,
) -> dict:
    """
    חיזוי what-if:
      delta_pct — שינוי שנתי נוסף מעבר למגמה (למשל 5.0 = +5% לשנה)
      years_ahead — כמה שנים קדימה להקרין

    Returns:
    {
      "indicator": { code, name_he, unit },
      "historical": [{ year, value }],
      "forecast": [{ year, value, is_forecast }],
      "base_slope": float,
      "delta_pct": float,
    }
    """
    rows = (
        db.query(DataPoint, Indicator)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(
            and_(
                DataPoint.municipality_id == municipality_id,
                Indicator.code == indicator_code,
                DataPoint.value.isnot(None),
            )
        )
        .order_by(DataPoint.year)
        .all()
    )

    if len(rows) < 2:
        return {"error": "אין מספיק נתונים היסטוריים"}

    years = np.array([dp.year for dp, _ in rows])
    values = np.array([dp.value for dp, _ in rows])
    ind = rows[0][1]

    # fit linear trend
    slope, intercept = np.polyfit(years, values, 1)
    last_year = int(years[-1])
    last_value = float(values[-1])

    historical = [{"year": int(y), "value": float(v), "is_forecast": False} for y, v in zip(years, values)]

    # הקרנה: trend + delta
    delta_per_year = last_value * (delta_pct / 100)
    forecast_points = []
    for i in range(1, years_ahead + 1):
        y = last_year + i
        projected = intercept + slope * y + delta_per_year * i
        forecast_points.append({"year": y, "value": round(projected, 2), "is_forecast": True})

    return {
        "indicator": {"code": ind.code, "name_he": ind.name_he, "unit": ind.unit},
        "historical": historical,
        "forecast": historical + forecast_points,
        "base_slope": round(float(slope), 4),
        "delta_pct": delta_pct,
    }
```

**הוסף ל-`backend/app/routers/analytics.py`:**
```python
from app.services.analytics import whatif

@router.get("/forecast/{municipality_id}")
def forecast(
    municipality_id: int,
    indicator_code: str,
    delta_pct: float = 0.0,
    years_ahead: int = 5,
    db: Session = Depends(get_db),
):
    """
    חיזוי what-if.
    GET /api/v1/analytics/forecast/504?indicator_code=POP_TOTAL&delta_pct=2.5&years_ahead=5
    """
    return whatif.forecast(db, municipality_id, indicator_code, delta_pct, years_ahead)
```

**אימות:**
```bash
curl "localhost:8000/api/v1/analytics/forecast/504?indicator_code=POP_TOTAL&delta_pct=0&years_ahead=5"
# → { historical: [...13 points], forecast: [...18 points], base_slope: 51246 }

curl "localhost:8000/api/v1/analytics/forecast/504?indicator_code=POP_TOTAL&delta_pct=3.0"
# → forecast values ~3% higher per year vs base
```

---

### 5.6 — ScenarioBuilder.jsx + ForecastChart.jsx (Frontend)

> ✅ הושלם — 2026-05-10 — ForecastChart.jsx + ForecastPage.jsx נוצרו. App.jsx עודכן עם routes /map + /forecast. api/client.js עודכן עם getChoroplethGeoJSON + downloadPDF + getForecast. Build עבר (605 modules).

**מה עושים:** דף תחזיות — בחר רשות + מדד + גרור סליידר delta% → גרף מציג היסטוריה + תחזית

**הוסף ל-`frontend/src/api/client.js`:**
```js
getForecast: (municipalityId, indicatorCode, deltaPct = 0, yearsAhead = 5) =>
  get(`/analytics/forecast/${municipalityId}?indicator_code=${indicatorCode}&delta_pct=${deltaPct}&years_ahead=${yearsAhead}`),
```

**`frontend/src/components/charts/ForecastChart.jsx`:**
```jsx
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'

export function ForecastChart({ data }) {
  const lastHistoricalYear = data.historical.at(-1)?.year

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-lg font-semibold mb-1" dir="rtl">
        {data.indicator.name_he}
        {data.delta_pct !== 0 && (
          <span className="text-sm font-normal text-blue-600 mr-2">
            (תרחיש: {data.delta_pct > 0 ? '+' : ''}{data.delta_pct}% לשנה)
          </span>
        )}
      </h2>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data.forecast}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={v => v.toLocaleString('he-IL')} />
          <Tooltip formatter={v => v.toLocaleString('he-IL')} />
          <Legend />
          <ReferenceLine x={lastHistoricalYear} stroke="#9ca3af" strokeDasharray="4 4" label="היום" />
          <Line
            dataKey="value"
            name={data.indicator.name_he}
            stroke="#2563eb"
            strokeWidth={2}
            dot={({ payload }) => payload.is_forecast
              ? <circle key={payload.year} cx={0} cy={0} r={4} fill="#f59e0b" />
              : <circle key={payload.year} cx={0} cy={0} r={3} fill="#2563eb" />
            }
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2 text-right">
        עיגולים כחולים = היסטוריה · עיגולים כתומים = תחזית · קו מקווקוו = גבול התחזית
      </p>
    </div>
  )
}
```

**`frontend/src/pages/ForecastPage.jsx`:**
```jsx
import { useState, useEffect } from 'react'
import { MunicipalitySelector } from '../components/selectors/MunicipalitySelector'
import { ForecastChart } from '../components/charts/ForecastChart'
import { api } from '../api/client'

export function ForecastPage() {
  const [muni, setMuni] = useState(null)
  const [indicators, setIndicators] = useState([])
  const [indicatorCode, setIndicatorCode] = useState('POP_TOTAL')
  const [deltaPct, setDeltaPct] = useState(0)
  const [yearsAhead, setYearsAhead] = useState(5)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.getIndicators().then(setIndicators) }, [])

  useEffect(() => {
    if (!muni || !indicatorCode) return
    setLoading(true)
    api.getForecast(muni.id, indicatorCode, deltaPct, yearsAhead)
      .then(setData)
      .finally(() => setLoading(false))
  }, [muni, indicatorCode, deltaPct, yearsAhead])

  return (
    <div className="p-6 max-w-4xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">תחזיות What-If</h1>

      <div className="bg-white rounded-xl shadow p-4 flex gap-4 flex-wrap items-end mb-6">
        <div className="flex-1 min-w-48">
          <label className="text-sm text-gray-500 block mb-1">רשות</label>
          <MunicipalitySelector value={muni} onChange={setMuni} />
        </div>
        <div className="flex-1">
          <label className="text-sm text-gray-500 block mb-1">מדד</label>
          <select
            value={indicatorCode}
            onChange={e => setIndicatorCode(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 bg-white text-sm"
          >
            {indicators.flatMap(d =>
              d.indicators.map(ind => (
                <option key={ind.code} value={ind.code}>{ind.name_he}</option>
              ))
            )}
          </select>
        </div>
        <div>
          <label className="text-sm text-gray-500 block mb-1">שנות תחזית</label>
          <select
            value={yearsAhead}
            onChange={e => setYearsAhead(Number(e.target.value))}
            className="border rounded-lg px-3 py-2 bg-white text-sm"
          >
            {[3, 5, 10].map(y => <option key={y} value={y}>{y} שנים</option>)}
          </select>
        </div>
      </div>

      {/* סליידר delta */}
      <div className="bg-white rounded-xl shadow p-4 mb-6">
        <label className="text-sm font-medium text-gray-700 block mb-3">
          שינוי שנתי נוסף מעבר למגמה:
          <span className={`mr-2 font-bold ${deltaPct > 0 ? 'text-green-600' : deltaPct < 0 ? 'text-red-600' : 'text-gray-500'}`}>
            {deltaPct > 0 ? '+' : ''}{deltaPct}%
          </span>
        </label>
        <input
          type="range"
          min="-10"
          max="10"
          step="0.5"
          value={deltaPct}
          onChange={e => setDeltaPct(Number(e.target.value))}
          className="w-full accent-blue-600"
          dir="ltr"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>-10%</span>
          <span>0%</span>
          <span>+10%</span>
        </div>
      </div>

      {loading && <div className="text-center text-gray-400 py-8">טוען תחזית...</div>}
      {data && !data.error && <ForecastChart data={data} />}
      {data?.error && <p className="text-center text-red-500">{data.error}</p>}
    </div>
  )
}
```

**עדכון `frontend/src/App.jsx`:**
```jsx
import { ForecastPage } from './pages/ForecastPage'
// בnavbar:
<NavLink to="/forecast" ...>תחזיות</NavLink>
// בRoutes:
<Route path="/forecast" element={<ForecastPage />} />
```

**אימות:** בחר "תל אביב-יפו" + "אוכלוסייה" → גרף מגמה + 5 שנות תחזית → גרור סליידר ל-+3% → הגרף מתעדכן

---

## סיכום שלב 5

| תת-שלב | קבצים עיקריים | אימות | סטטוס |
|--------|--------------|-------|--------|
| 5.1 | `services/export/geojson_builder.py` + `routers/export.py` | `GET /export/geojson?indicator_code=POP_TOTAL&year=2022` → FeatureCollection עם value | ⬜ |
| 5.2 | `ChoroplethMap.jsx` + `MapPage.jsx` | `/map` → מפה ישראל צבועה + tooltip | ⬜ |
| 5.3 | `services/export/pdf_builder.py` + עדכון export router | `GET /export/pdf/504?year=2022` → PDF עברי עם טבלאות + גרפים | ⬜ |
| 5.4 | עדכון `DashboardPage.jsx` + `client.js` | לחיצה על "ייצא PDF" → קובץ מורד | ⬜ |
| 5.5 | `services/analytics/whatif.py` + עדכון analytics router | `GET /analytics/forecast/504?indicator_code=POP_TOTAL&delta_pct=3` → תחזית | ⬜ |
| 5.6 | `ForecastChart.jsx` + `ForecastPage.jsx` | `/forecast` → גרף + סליידר delta → תחזית מתעדכנת | ⬜ |

**סדר ביצוע מומלץ:** 5.1 → 5.2 (מפה עצמאית) ‖ 5.3 → 5.4 (PDF עצמאי) ‖ 5.5 → 5.6 (תחזיות עצמאיות)  
שלושת המסלולים עצמאיים — אפשר לבצע בכל סדר או במקביל.

**דרישות מוקדמות:**
- `frontend/public/israel_municipalities.geojson` — קובץ גאוגרפי עם `muni_code` ב-properties
- גופן `backend/app/services/export/fonts/DavidLibre-Regular.ttf`
- `pip install reportlab arabic-reshaper python-bidi matplotlib shapely`
