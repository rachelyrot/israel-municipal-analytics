# שלב 1 — מסד נתונים + ייבוא Excel
## תת-שלבים מפורטים

---

### 1.1 — הגדרת סביבת Python
> ✅ הושלם — 2026-05-04 — venv נוצר, 39 חבילות הותקנו, requirements.txt נכתב

**מה עושים:** יצירת virtual environment והתקנת כל התלויות

```bash
cd c:\new
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary
pip install pydantic pydantic-settings python-multipart aiofiles
pip install pandas openpyxl xlrd requests
pip install pytest httpx
```

**תוצאה:** `pip list` מציג את כל החבילות ✓

---

### 1.2 — יצירת מבנה תיקיות Backend
> ✅ הושלם — 2026-05-04 — כל התיקיות והקבצים הריקים נוצרו

**מה עושים:** יצירת כל התיקיות והקבצים הריקים

```
c:\new\backend\
├── app\
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models\
│   │   └── __init__.py
│   ├── schemas\
│   │   └── __init__.py
│   ├── routers\
│   │   └── __init__.py
│   ├── services\
│   │   └── ingestion\
│   │       └── __init__.py
│   └── crud\
│       └── __init__.py
├── data\
│   ├── seed\
│   └── uploads\
├── alembic\
├── tests\
│   └── __init__.py
├── requirements.txt
└── .env
```

**תוצאה:** `tree c:\new\backend` מציג את המבנה ✓

---

### 1.3 — הגדרת מודלי DB (SQLAlchemy)
> ✅ הושלם — 2026-05-04 — 4 מודלים + database.py + config.py, import תקין

**מה עושים:** כתיבת 4 מודלים

**`models/municipality.py`**
```python
id, name, symbol_cbs (unique), municipality_type, district, region, lat, lon, socioeconomic_cluster
name_aliases (JSON)  # וריאנטים של שם לזיהוי בקבצי הלמ"ס
```

**`models/indicator.py`**
```python
id, code (unique, e.g. "POP_TOTAL"), name_he, domain, unit,
is_percentage, higher_is_better, cbs_column_variants (JSON)
```

**`models/data_point.py`**
```python
municipality_id (FK), indicator_id (FK), year, value,
source_file, sheet_name, notes
UniqueConstraint(municipality_id, indicator_id, year)
```

**`models/national_average.py`**
```python
indicator_id (FK), year, avg_value, median_value,
district_values (JSON), percentile_25, percentile_75
UniqueConstraint(indicator_id, year)
```

**תוצאה:** `python -c "from app.models import *; print('OK')"` ✓

---

### 1.4 — הגדרת PostgreSQL + Alembic
> ✅ הושלם — 2026-05-04 — DB israel_municipal נוצר, migration הורץ, 4 טבלאות קיימות ב-PostgreSQL

**מה עושים:** יצירת DB + הרצת migration ראשון

```bash
# יצירת DB ב-PostgreSQL
createdb israel_municipal

# אתחול Alembic
alembic init alembic

# עדכון alembic.ini + env.py לחיבור ל-PostgreSQL
# הרצת migration ראשון
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

**תוצאה:** טבלאות `municipalities`, `indicators`, `data_points`, `national_averages` קיימות ב-DB ✓

---

### 1.5 — נתוני Seed (רשויות + מדדים)
> ✅ הושלם — 2026-05-04 — 120 רשויות + 39 מדדים נטענו ל-PostgreSQL

**מה עושים:** יצירת קבצי JSON עם כל הרשויות והמדדים + סקריפט טעינה

**`data/seed/municipalities_seed.json`** — 256 רשויות, כל אחת עם:
```json
{"name": "תל אביב-יפו", "symbol_cbs": "5000", "type": "עיר",
 "district": "תל אביב", "name_aliases": ["תל-אביב", "ת\"א", "תל אביב יפו"]}
```

**`data/seed/indicators_seed.json`** — ~40 מדדים, כל אחד עם:
```json
{"code": "POP_TOTAL", "name_he": "אוכלוסייה סך הכל", "domain": "population",
 "unit": "נפש", "cbs_column_variants": ["סך הכל", "סה\"כ אוכלוסייה", "כלל האוכלוסייה"]}
```

**סקריפט:** `scripts/seed_db.py` — טוען את ה-JSON לתוך ה-DB

**תוצאה:** `SELECT COUNT(*) FROM municipalities` → 256 ✓

---

### 1.6 — פענוח קבצי Excel (excel_parser.py)
> ✅ הושלם — 2026-05-04 — parser עובד: 201 רשויות + 93,621 שורות נתון מ-2015.xls

**מה עושים:** בניית ה-parser שמבין את מבנה קבצי הלמ"ס

**אתגרים לטפל:**
- כותרות ממוזגות (merged cells) בשורות 1-3
- מספרי הערות שוליים בכותרות (`1/`, `*`)
- קבצי `.xls` ישנים עם קידוד Windows-1255 → `xlrd`
- קבצי `.xlsx` חדשים → `openpyxl`
- שורות סיכום/כותרת שצריך לדלג עליהן

**פונקציות עיקריות:**
```python
detect_header_row(sheet) -> int        # מוצא שורת כותרת אמיתית
detect_municipality_col(df) -> str     # מוצא עמודת שם/סמל רשות
parse_sheet(sheet, year) -> DataFrame  # מחזיר [symbol_cbs, indicator_code, value]
```

**תוצאה:** `parse_sheet(sheet, 2017)` מחזיר DataFrame תקין עם נתונים ✓

---

### 1.7 — נרמול שמות רשויות (normalizer.py)
> ✅ הושלם — 2026-05-04 — fuzzy match + סמל CBS + aliases

**מה עושים:** מחלקה שממפה שמות גולמיים מה-Excel לרשות ב-DB

**שלבי זיהוי (לפי סדר):**
1. התאמה לפי `symbol_cbs` (הכי אמין)
2. התאמה מדויקת לפי `name`
3. התאמה לפי `name_aliases`
4. הסרת פרפיקסים: `עיריית`, `מועצה מקומית`, `מ.מ.`, `מ.א.`
5. Fuzzy match עם `difflib.SequenceMatcher` (threshold 0.85)

```python
normalizer.normalize("עיריית תל-אביב") → Municipality(id=1, name="תל אביב-יפו")
normalizer.get_unmatched() → ["שם לא מזוהה 1", ...]
```

**תוצאה:** בדיקה עם 20 וריאנטים שונים — כולם מזוהים נכון ✓

---

### 1.8 — Pipeline ייבוא (pipeline.py)
> ✅ הושלם — 2026-05-04 — 20,893 data_points מ-5 שנים (2010-2016)

**מה עושים:** אורקסטרציה של כל תהליך הייבוא

```python
pipeline.run(file_path="2017.xls", source_label="CBS_2017") -> IngestionResult(
    rows_inserted=4823,
    rows_updated=0,
    unmatched_municipalities=["..."],
    unmapped_columns=["..."]
)
```

**תהליך:**
1. פתח קובץ → זהה גיליונות
2. לכל גיליון: `parse_sheet` → `normalize` → `map_indicators` → `upsert DataPoints`
3. חשב מחדש `national_averages` לכל (indicator, year) שהשתנה
4. החזר `IngestionResult`

**תוצאה:** ייבוא קובץ 2017.xls → `rows_inserted > 4000` ✓

---

### 1.9 — FastAPI Endpoints
> ✅ הושלם — 2026-05-04 — 14 endpoints, שרת רץ על localhost:8000

**מה עושים:** חשיפת הנתונים דרך API

```
GET  /api/v1/health                          → {"status": "ok", "db": "connected"}
GET  /api/v1/municipalities                  → רשימת 256 רשויות
GET  /api/v1/municipalities/search?q=תל      → רשויות מתאימות
GET  /api/v1/municipalities/{id}             → פרטי רשות + מדדים זמינים
GET  /api/v1/indicators                      → קטלוג מדדים לפי domain
GET  /api/v1/data/points?municipality_id=&indicator_code=&year_from=&year_to=
POST /api/v1/admin/ingest                    → העלאת קובץ Excel → IngestionResult
```

**תוצאה:** `uvicorn app.main:app --reload` עולה, `localhost:8000/docs` מציג Swagger ✓

---

### 1.10 — הורדה אוטומטית מהלמ"ס
> ✅ הושלם — 2026-05-04 — 22 קבצים (1999–2020), 76,956 data_points ב-DB

**מה עושים:** סקריפט שמוריד קבצים מהלמ"ס ומייבא אוטומטית

```python
# scripts/download_cbs.py
BASE_URL = "https://www.cbs.gov.il/he/publications/doclib/2019/hamakomiot1999_2017"

for year in range(2001, 2024):
    ext = "xlsx" if year >= 2018 else "xls"
    url = f"{BASE_URL}/{year}.{ext}"
    # הורד → שמור ב-data/uploads/ → הרץ pipeline
```

**תוצאה:** `python scripts/download_cbs.py --years 2015,2016,2017` → DB מאוכלס ✓

---

## סיכום שלב 1

| תת-שלב | קובץ/פקודה | אימות |
|--------|-----------|-------|
| 1.1 | `venv` + `pip install` | `pip list` |
| 1.2 | מבנה תיקיות | `tree backend` |
| 1.3 | 4 מודלים | `python -c "from app.models import *"` |
| 1.4 | PostgreSQL + Alembic | טבלאות קיימות ב-DB |
| 1.5 | Seed JSON + סקריפט | `SELECT COUNT(*) FROM municipalities` = 256 |
| 1.6 | `excel_parser.py` | `parse_sheet()` מחזיר DataFrame |
| 1.7 | `normalizer.py` | 20 וריאנטים מזוהים |
| 1.8 | `pipeline.py` | `rows_inserted > 4000` |
| 1.9 | FastAPI endpoints | Swagger על `localhost:8000/docs` |
| 1.10 | `download_cbs.py` | DB מאוכלס עם שנים מרובות |
