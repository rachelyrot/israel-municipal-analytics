# פלטפורמת ניתוח רשויות מקומיות — תכנית יישום

## מקור נתונים
הלמ"ס: "הרשויות המקומיות בישראל — קובצי נתונים לעיבוד 1999–2023"

**תבנית URL ישירה לכל שנה (מאושר ✓):**
- עד ~2017: `https://www.cbs.gov.il/he/publications/doclib/2019/hamakomiot1999_2017/{שנה}.xls`
- 2018+: `https://www.cbs.gov.il/he/publications/doclib/2019/hamakomiot1999_2017/{שנה}.xlsx`
- בדוק ועובד: `2001.xls` (1.3MB) ✓, `2020.xlsx` (1MB) ✓
- הורדה: `requests.get(url)` — ללא צורך באימות

**מבנה כל קובץ Excel:**
- גיליון אחד לכל נושא (לוח)
- עמודה א: סמל הרשות (קוד CBS), עמודה ב: שם הרשות
- שורות = רשויות, עמודות = מדדים
- כותרות מרובות שורות + תאים ממוזגים (אתגר בפענוח)
- קבצי `.xls` ישנים = קידוד Windows-1255

**נושאי הלוחות (גיליונות) בכל קובץ:**
| לוח | נושא | מדדים עיקריים |
|-----|------|----------------|
| 1 | נתונים כלליים | שטח, מעמד מוניציפלי, אשכול חברתי-כלכלי |
| 2 | אוכלוסייה | סך, גיל, מין, צפיפות |
| 3 | גידול טבעי ועלייה | לידות, פטירות, עלייה, ירידה |
| 4 | תעסוקה | שיעור תעסוקה, שכר, ענפים |
| 5 | חינוך | תלמידים, מורים, בגרות, נשירה |
| 6 | רווחה | קצבאות, סיוע, זקנה |
| 7 | תקציב | הכנסות, הוצאות, גירעון לנפש |
| 8 | ארנונה | תעריפים, גביה, פטורים |
| 9 | תשתיות | מים, ביוב, חשמל |
| 10 | בנייה | היתרים, דירות חדשות |

## סטאק
- Backend: Python + FastAPI + **PostgreSQL** (SQLAlchemy + Alembic)
- Frontend: React + Vite + TypeScript + TailwindCSS + Recharts + Leaflet
- AI: Claude API (עברית)
- מתאים לעשרות משתמשים בו-זמנית

---

## שלב 1 — מסד נתונים + ייבוא Excel

**מה בונים:** סכמת DB + pipeline שמייבא קבצי הלמ"ס לתוך DB מסודר

**קבצים:**
```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/municipality.py      # id, name, symbol_cbs, type, district, lat, lon
│   ├── models/indicator.py         # code, name_he, domain, unit, cbs_column_variants
│   ├── models/data_point.py        # municipality_id, indicator_id, year, value, source_file
│   ├── models/national_average.py  # indicator_id, year, avg, district_values (JSON)
│   ├── services/ingestion/
│   │   ├── normalizer.py           # נרמול שמות רשויות (fuzzy match)
│   │   ├── excel_parser.py         # פענוח מבנה קבצי הלמ"ס
│   │   └── pipeline.py             # run(file_path) → IngestionResult
│   └── routers/
│       ├── municipalities.py       # GET /municipalities, /municipalities/search
│       ├── indicators.py           # GET /indicators
│       ├── data.py                 # GET /data/points
│       └── admin.py                # POST /admin/ingest
├── data/seed/
│   ├── municipalities_seed.json    # 256 רשויות + סמל CBS
│   └── indicators_seed.json        # ~40 מדדים, 7 תחומים
└── requirements.txt
```

**אימות:** POST קובץ Excel → `rows_inserted > 0`, GET `/municipalities` → 256 רשויות

---

## שלב 2 — דשבורד בסיסי

**מה בונים:** React app עם בחירת רשות + שנה + כרטיסי KPI + גרף רב-שנתי

**קבצים:**
```
frontend/src/
├── api/client.ts + types.ts
├── store/dashboardStore.ts         # Zustand: רשות, שנה, תחום
├── components/
│   ├── selectors/MunicipalitySelector.tsx
│   ├── selectors/YearSelector.tsx
│   ├── kpi/KPICard.tsx             # ערך + מגמה + vs ממוצע ארצי
│   ├── kpi/KPIGrid.tsx
│   └── charts/TimeSeriesChart.tsx  # Recharts LineChart + קו ממוצע ארצי
└── pages/DashboardPage.tsx
```

**API חדש:** `GET /data/kpis/{id}?year=&domain=` | `GET /data/timeseries/{id}?...`

**אימות:** בחר "תל אביב-יפו" 2022 → KPI cards + גרף מוצגים

---

## שלב 3 — השוואה + ניתוח

**מה בונים:** השוואת רשויות, מציאת רשויות דומות, דירוגים, מגמות

**Backend:**
```
services/analytics/
├── comparison.py    # מטריצת השוואה: ערך + דירוג + vs ממוצע
├── similarity.py    # מרחק אוקלידי על 5 מדדי בסיס → רשויות דומות
├── trends.py        # linear regression → direction + label בעברית
└── rankings.py      # דירוג לפי מדד / שנה / מחוז / סוג
```

**Frontend:** `ComparisonPage` (RadarChart), `RankingsPage`, `SimilarMunicipalities` panel

**API:** `GET /analytics/compare` | `/analytics/similar/{id}` | `/analytics/rankings`

---

## שלב 4 — AI בעברית

**מה בונים:** שאלות בשפה חופשית → Claude → תשובה מבוססת נתונים בלבד

**כלל ברזל:** Claude מקבל context עם נתונים אמיתיים מה-DB לפני כל תשובה — לא ממציא כלום

```
services/ai/
├── claude_client.py    # Anthropic SDK + prompt caching על system prompt
├── query_engine.py     # שאלה → שליפת נתונים → context → Claude → תשובה + מקורות
├── context_builder.py  # בניית טבלת נתונים עברית מה-DB
└── insight_generator.py # Python מחשב חריגות/מגמות → Claude מנסח בעברית
```

**API:** `POST /ai/query` (session_id, municipality_id?) | `GET /ai/insights/{id}`

**UI:** `AIQueryPage` — תיבת שאלה + תשובה + ציטוטי מקור

---

## שלב 5 — מפות + PDF + תחזיות

**מה בונים:** מפה כורופלת, ייצוא PDF בעברית, תרחישי What-If

**מפה:**
- `frontend/public/israel_municipalities.geojson` (נתוני CBS פתוחים)
- `ChoroplethMap.tsx` — react-leaflet + צביעה לפי ערכים (5 דליים קוונטיל)
- `geojson_builder.py` — מיזוג DataPoints לתוך GeoJSON לפי CBS symbol

**PDF:**
- ReportLab + `arabic-reshaper` + `python-bidi` (עברית תקינה)
- גופן: `DavidLibre-Regular.ttf`
- גרפים מ-matplotlib (לא Recharts — backend בלבד)

**What-If:**
- `whatif.py`: fit linear trend + modification shift + project 5 years forward
- `ScenarioBuilder.tsx` + `ForecastChart.tsx`

---

## סדר עבודה

| שלב | משך | תוצאה ניתנת לבדיקה |
|-----|-----|---------------------|
| 1   | יום 1-2 | ייבוא Excel → DB + API |
| 2   | יום 3-4 | דשבורד עם KPIs וגרפים |
| 3   | יום 5-6 | השוואה + דירוגים |
| 4   | יום 7   | שאלות AI בעברית |
| 5   | יום 8-9 | מפה + PDF + תחזיות |

## הערות Windows 10
- `pathlib.Path` בכל מקום בPython
- `xlrd` לקבצי `.xls` ישנים של הלמ"ס
- uvicorn עם `--workers 4` (PostgreSQL תומך בריבוי workers)
- Vite proxy: `/api` → `localhost:8000`
- PostgreSQL: התקנה חד-פעמית דרך installer רשמי
- `DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/israel_municipal`
- `pip install psycopg2-binary` (במקום sqlite)
