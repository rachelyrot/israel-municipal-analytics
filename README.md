<div align="center">

# 🏛️ Israel Municipal Analytics

### Analytics platform for Israel's local municipalities

Ingests ~25 years of **Israel Central Bureau of Statistics (CBS)** data and exposes it through an interactive dashboard, with natural-language querying powered by Claude.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Claude](https://img.shields.io/badge/AI-Claude-D97757?logo=anthropic&logoColor=white)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

<img src="frontend/src/assets/hero.png" alt="Israel Municipal Analytics — dashboard preview" width="800"/>

</div>

---

## Overview

**Israel Municipal Analytics** turns raw CBS Excel exports (1999–2024) — with all the inconsistency typical of decades-old government spreadsheets — into a clean, queryable dataset covering all 272 Israeli local authorities. On top of that data sits a full REST API and a React dashboard (Hebrew/RTL) for exploring, comparing, and asking questions about population, employment, education, welfare, budget, and infrastructure indicators for any municipality — including a free-form Hebrew chat interface backed by Claude, with context-aware follow-ups and per-session memory.

## Features

| | |
|---|---|
| 📊 **Interactive dashboard** | Rank municipalities by indicator and year; rich per-municipality profile (KPI grid, percentage bars, radar chart, land-use donut) |
| 🔍 **Cross-domain indicator search** | Search any indicator by name and jump straight to its domain tab and chart |
| 📈 **Multi-municipality comparison** | Compare an unlimited number of municipalities over time against national, district, and municipality-type averages |
| 🤖 **Hebrew AI querying** | Multi-turn chat with Claude that understands follow-up questions, tracks the active municipality/year, and surfaces automatic insights on deviations from the national average |
| 🗺️ **Choropleth-ready map data** | GeoJSON export built from municipality coordinates |
| 📄 **Hebrew PDF export** | Full RTL PDF report for any municipality |
| 🔮 **What-if forecasting** | Linear trend projection with optional percentage-delta simulation |
| 🧮 **Similarity search** | Euclidean-distance matching on core indicators to surface comparable municipalities |

## Architecture

```mermaid
flowchart LR
    A["CBS Excel files<br/>1999–2024"] --> B["Ingestion pipeline<br/>excel_parser · normalizer · pipeline"]
    B --> C[("PostgreSQL<br/>municipalities · indicators · data_points")]
    C --> D["FastAPI<br/>7 routers · /api/v1"]
    D --> E["React + Vite + Tailwind<br/>Dashboard · Analytics · AI Chat"]
    D --> F["Claude API<br/>Hebrew chat + generated insights"]
```

**Data flow:** CBS Excel file → `excel_parser.py` (parsing, cleanup) → `normalizer.py` (fuzzy municipality-name matching) → `pipeline.py` (upsert + national-average recomputation) → PostgreSQL.

## Tech stack

**Backend** — FastAPI · SQLAlchemy · Alembic · PostgreSQL · pandas · openpyxl/xlrd · Anthropic SDK · ReportLab (Hebrew PDF generation)
**Frontend** — React 19 · Vite · Tailwind CSS v4 · Zustand · Recharts · React-Leaflet · React Router

## Getting started

Requires Python 3.11+, Node 18+, PostgreSQL 14+.

### 1. Database

```sql
CREATE DATABASE israel_municipal;
```

### 2. Backend

```bash
python -m venv venv
venv\Scripts\activate          # Windows

cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@127.0.0.1:5432/israel_municipal
ANTHROPIC_API_KEY=sk-ant-...
```

> **Windows note:** use `127.0.0.1`, not `localhost` — psycopg2 can resolve `localhost` to IPv6, which fails PostgreSQL authentication.

```bash
alembic upgrade head
python scripts/seed_db.py
python scripts/seed_coordinates.py    # populates lat/lon — required for map + PDF
python scripts/auto_ingest.py         # ingests any CBS file in data/uploads/ not yet in the DB
uvicorn app.main:app --reload         # http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
```

Interactive API docs are served at `http://localhost:8000/docs`.

## Application pages

| Page | Description |
|------|-------------|
| **Dashboard** (`/app/`) | Ranked list of all municipalities by indicator/year alongside a full municipality profile |
| **Analytics** (`/app/analytics`) | Unlimited multi-municipality comparison by domain, with national/district/type averages |
| **Ask AI** (`/app/ai`) | Multi-turn Hebrew chat with Claude over municipal data |

## Core API surface

```
GET  /api/v1/municipalities/search?q=tel
GET  /api/v1/indicators?year=2022
GET  /api/v1/data/kpis/{municipality_id}?year=2022&domain=population
GET  /api/v1/data/timeseries/{municipality_id}/single?indicator_code=POP_TOTAL
GET  /api/v1/analytics/compare?municipality_ids=1,2&indicator_code=POP_TOTAL
GET  /api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022
GET  /api/v1/analytics/trends/{municipality_id}?indicator_code=POP_TOTAL
GET  /api/v1/analytics/forecast/{municipality_id}
GET  /api/v1/export/geojson
GET  /api/v1/export/pdf/{municipality_id}
POST /api/v1/ai/query
POST /api/v1/admin/ingest        # manual Excel upload
```

## Project structure

```
backend/
├── app/
│   ├── routers/          # municipalities · indicators · data · admin · analytics · ai · export
│   ├── models/            # 4 SQLAlchemy tables
│   └── services/
│       ├── ingestion/     # excel_parser · normalizer · pipeline
│       ├── analytics/     # comparison · similarity · trends · rankings · whatif
│       ├── ai/            # claude_client · context_builder · query_engine · insight_generator
│       └── export/        # geojson_builder · pdf_builder
├── data/seed/              # municipalities_seed.json · indicators_seed.json
├── data/uploads/            # source CBS files (cbs_<year>.xls/xlsx)
└── scripts/                 # ingestion, seeding, diagnostics, maintenance

frontend/
└── src/
    ├── pages/               # Dashboard · Analytics · AIQuery
    ├── components/          # KPI grid, charts, selectors, maps
    ├── store/                # Zustand (dashboardStore)
    └── api/client.js         # fetch wrapper for /api/v1
```

## Data

- Source: [CBS — Local Authorities in Israel](https://www.cbs.gov.il/he/publications/Pages/2024/הרשויות-המקומיות-בישראל-קובצי-נתונים-לעיבוד-1999-2023.aspx)
- 272 local authorities
- ~60 indicators across population, employment, education, budget, taxation, welfare, infrastructure, and more
- Coverage: 1999–2024, ingested automatically via `auto_ingest.py`

## Project status

- ✅ Stage 1 — database + ingestion
- ✅ Stage 2 — dashboard
- ✅ Stage 3 — comparison, similarity, trends, rankings
- ✅ Stage 4 — Hebrew AI querying
- ✅ Stage 5 — choropleth map data, PDF export, what-if forecasting

## License

Released under the [MIT License](LICENSE).
