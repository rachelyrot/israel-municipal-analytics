# ניתוח רשויות מקומיות בישראל

פלטפורמת ניתוח נתונים של הרשויות המקומיות בישראל, מבוססת על קבצי הלמ"ס 1999–2024.  
Backend: Python + FastAPI + PostgreSQL | Frontend: React + Vite + Tailwind + Recharts

---

## דרישות מוקדמות

| תוכנה | גרסה מינימלית |
|-------|--------------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |

---

## התקנה

### 1. מסד נתונים

התקן PostgreSQL וצור מסד נתונים:
```sql
CREATE DATABASE israel_municipal;
```

### 2. Backend

```bash
# צור וירטואל אנביירונמנט
python -m venv venv

# הפעל (Windows)
venv\Scripts\activate

# התקן תלויות
cd backend
pip install -r requirements.txt

# צור קובץ .env
copy .env.example .env
# ערוך את .env עם הסיסמה שלך:
# DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/israel_municipal

# הרץ migrations
alembic upgrade head

# זרע את מסד הנתונים (רשויות + מדדים)
python scripts/seed_db.py
```

### 3. ייבוא נתוני הלמ"ס

הורד את קבצי Excel מאתר הלמ"ס ושמור אותם בתיקייה `backend/data/uploads/`  
בפורמט: `cbs_2020.xlsx`, `cbs_2019.xlsx`, ... (xls לשנים עד 2015)

לאחר מכן הרץ:
```bash
python scripts/reingest_all.py
```

### 4. Frontend

```bash
cd frontend
npm install
```

---

## הפעלה

**Backend** (מתוך `backend/` עם venv פעיל):
```bash
uvicorn app.main:app --reload
# רץ על http://localhost:8000
```

**Frontend** (מתוך `frontend/`):
```bash
npm run dev
# רץ על http://localhost:5173
```

פתח את הדפדפן על `http://localhost:5173`

---

## מה יש בפרויקט

### דפים

| דף | תיאור |
|----|-------|
| **דשבורד** | בחר רשות + שנה → כרטיסי KPI + גרף רב-שנתי |
| **השוואה** | השווה 2 רשויות על אותו מדד לאורך זמן |
| **דירוגים** | דירוג כל הרשויות לפי מדד ושנה, עם סינון לפי מחוז |

### API Endpoints

```
GET  /api/v1/municipalities/search?q=תל
GET  /api/v1/indicators
GET  /api/v1/data/kpis/{municipality_id}?year=2022&domain=population
GET  /api/v1/data/timeseries/{municipality_id}/single?indicator_code=POP_TOTAL
GET  /api/v1/analytics/compare?municipality_ids=1,2&indicator_code=POP_TOTAL
GET  /api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022
GET  /api/v1/analytics/trends/{municipality_id}?indicator_code=POP_TOTAL
POST /api/v1/admin/ingest  (העלאת קובץ Excel ידנית)
```

תיעוד Swagger אוטומטי: `http://localhost:8000/docs`

### מבנה הפרויקט

```
backend/
├── app/
│   ├── models/          # SQLAlchemy: municipalities, indicators, data_points, national_averages
│   ├── routers/         # FastAPI routes
│   ├── services/
│   │   ├── ingestion/   # excel_parser → normalizer → pipeline
│   │   └── analytics/   # comparison, trends, rankings
│   └── main.py
├── data/
│   ├── seed/            # נתוני זריעה ראשוניים (256 רשויות, ~60 מדדים)
│   └── uploads/         # קבצי CBS (לא מועלים ל-Git)
└── scripts/
    ├── seed_db.py        # זריעת DB
    └── reingest_all.py   # ייבוא מחדש של כל הקבצים

frontend/src/
├── api/client.js         # fetch wrapper
├── store/                # Zustand state
├── components/           # KPICard, TimeSeriesChart, CompareChart, ...
└── pages/                # DashboardPage, ComparisonPage, RankingsPage
```

---

## נתונים

- מקור: [הלמ"ס — רשויות מקומיות בישראל](https://www.cbs.gov.il/he/publications/Pages/2024/הרשויות-המקומיות-בישראל-קובצי-נתונים-לעיבוד-1999-2023.aspx)
- 256 רשויות מקומיות
- ~60 מדדים: אוכלוסייה, תעסוקה, חינוך, תקציב, ארנונה, רווחה, תשתיות ועוד
- שנים: 1999–2024 (קבצי Excel שנתיים)
