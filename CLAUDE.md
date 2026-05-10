# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Israeli Municipal Analytics platform — ingests CBS (Central Bureau of Statistics) Excel files (1999–2023) into PostgreSQL and exposes a REST API. Frontend is React + Vite + Tailwind. UI is Hebrew/RTL.

## Backend Commands

All backend commands run from `c:\new\backend\` with the venv active:

```bash
# Activate venv (Windows) — venv lives at c:\new\venv\, not inside backend\
c:\new\venv\Scripts\activate

# Run dev server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"

# Seed DB (municipalities + indicators)
python scripts/seed_db.py

# Re-ingest all CBS files from data/uploads/ (naming: cbs_2020.xlsx)
python scripts/reingest_all.py

# Download + ingest CBS files
python scripts/download_cbs.py --years 2015,2016,2017

# Run tests
pytest
pytest tests/test_specific.py::test_name
```

## Frontend Commands

```bash
cd c:\new\frontend
npm run dev      # localhost:5173 (proxy: /api → localhost:8000)
npm run build
npm run lint
```

## Architecture

### Backend (`backend/app/`)

**Data flow:** CBS Excel file → `excel_parser.py` → `normalizer.py` → `pipeline.py` → PostgreSQL

- `main.py` — FastAPI app, CORS for localhost:5173/3000, mounts 7 routers under `/api/v1/`
- `database.py` — SQLAlchemy engine + `get_db()` dependency
- `config.py` — pydantic-settings, reads `.env`; fields: `database_url`, `app_name`, `debug`, `anthropic_api_key`

**4 core tables:**
- `municipalities` — 256 Israeli local authorities, each with `symbol_cbs` (CBS code), `name_aliases` (JSON for fuzzy match)
- `indicators` — ~60 indicators by domain (population/employment/education/welfare/budget/infrastructure/taxes), each with `cbs_column_variants` (JSON) for column matching
- `data_points` — time-series (municipality × indicator × year), unique constraint enforces last-write-wins via `ON CONFLICT DO UPDATE`
- `national_averages` — pre-computed avg/median/percentiles per (indicator, year), auto-refreshed on each ingestion

**Ingestion service (`services/ingestion/`):**
- `excel_parser.py` — handles `.xls` (xlrd, Windows-1255) and `.xlsx` (openpyxl), skips merged/footnote header rows; cleans values (`-`, `--`, `N/A`, `*` → None)
- `normalizer.py` — resolves raw municipality names: CBS symbol match → exact name → aliases → prefix stripping (`עיריית`, `מועצה מקומית`, etc.) → fuzzy (≥85%)
- `pipeline.py` — `run(file_path, year, db)` returns `IngestionResult`; calls `_recompute_national_averages()` after upsert; uploaded files land in `data/uploads/`

**Analytics service (`services/analytics/`):**
- `comparison.py` — multi-municipality comparison: same indicator, range of years, includes national avg series
- `similarity.py` — Euclidean distance on 5 base indicators (POP_TOTAL, EMP_RATE, BUDGET_PER_CAPITA, EDU_BAGRUT_RATE + socioeconomic_cluster), min-max normalized; returns similarity score 0–1
- `trends.py` — linear regression on time-series → slope, direction (`up`/`down`/`stable`), R², Hebrew label
- `rankings.py` — rank municipalities by indicator/year with optional district/type filter; ranking computed in Python after DB query (not SQL RANK())

**Export service (`services/export/`):**
- `geojson_builder.py` — builds Point GeoJSON from municipalities with lat/lon + DataPoints for chosen indicator/year
- `pdf_builder.py` — Hebrew PDF via ReportLab + `arabic-reshaper` + `python-bidi`; font at `services/export/fonts/DavidLibre-Regular.ttf`; map requires `python scripts/seed_coordinates.py` first

**Analytics service additions:**
- `whatif.py` — `forecast(db, muni_id, indicator_code, delta_pct, years_ahead)` → linear trend + optional per-year delta → `GET /analytics/forecast/{id}`

**AI service (`services/ai/`):**
- `claude_client.py` — singleton Anthropic client; `chat(question, context)` uses claude-haiku-4-5 with `cache_control: ephemeral` on the system prompt. Uses `httpx.Client(verify=False)` to bypass SSL inspection (NetFree workaround — do not remove).
- `context_builder.py` — `build_municipality_context(db, muni_id, year)` fetches all DataPoints + NationalAverages and formats as a Hebrew table (מדד | ערך | יחידה | ממוצע ארצי) grouped by domain; `build_comparison_context()` adds a column per municipality
- `insight_generator.py` — Python finds indicators where |deviation from national avg| ≥ 30%, then Claude formulates each as a single Hebrew sentence
- `query_engine.py` — `answer_question(...)` orchestrates: pick context builder → call Claude → return `{answer, sources, session_id, municipality_id, year}`

**Routers:**
- `municipalities.py` — GET `/municipalities`, `/municipalities/search?q=`, `/municipalities/{id}`
- `indicators.py` — GET `/indicators`, `/indicators/{code}`
- `data.py` — GET `/data/points`, `/data/kpis/{id}`, `/data/timeseries/{id}`, `/data/timeseries/{id}/single`, `/data/compare`
- `admin.py` — POST `/admin/ingest` (multipart: file + year)
- `analytics.py` — GET `/analytics/compare`, `/analytics/similar/{id}`, `/analytics/trends/{id}`, `/analytics/rankings`
- `ai.py` — POST `/ai/query` (free-form Hebrew question), GET `/ai/insights/{id}` (auto-generated anomaly insights)
- `export.py` — GET `/export/geojson` (choropleth GeoJSON from DB lat/lon), GET `/export/pdf/{id}` (Hebrew PDF with ReportLab)

### Database

```
DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal
ANTHROPIC_API_KEY=sk-ant-...
```

Single Alembic migration (`initial_schema`) covers all 4 tables. Swagger docs at `http://localhost:8000/docs`.

### Frontend (`frontend/src/`)

4 pages wired via react-router-dom, Hebrew RTL layout throughout:

- **DashboardPage** (`/`) — municipality + year selector → KPI cards + time-series chart + similar municipalities panel
- **ComparisonPage** (`/compare`) — select 2 municipalities + indicator → line chart overlay with national avg
- **RankingsPage** (`/rankings`) — select indicator + year + district filter → sorted table
- **MapPage** (`/map`) — choropleth map (react-leaflet circle markers, 5 quantile bins); side panel on click; requires lat/lon populated via `seed_coordinates.py`
- **ForecastPage** (`/forecast`) — What-If forecasts: select municipality + indicator + drag delta% slider → line chart with historical + projected values
- **AIQueryPage** (`/ai`) — free-form Hebrew question for a municipality + year; auto-loads anomaly insights; supports optional comparison municipalities; shows Claude's answer + collapsible data sources

Key components:
- `api/client.js` — fetch wrapper for all API calls; base path `/api/v1`; includes `aiQuery()`, `getInsights()`, `getChoroplethGeoJSON()`, `downloadPDF()`, `getForecast()`
- `store/dashboardStore.js` — Zustand: selectedMunicipality, selectedYear, selectedDomain, kpis; `fetchKPIs()` auto-triggered on selection change
- `components/charts/CompareChart.jsx` — merges multi-municipality series by year for Recharts LineChart
- `components/SimilarMunicipalities.jsx` — reads from analytics/similar, clicking a result updates the dashboard store

## Implementation Status

- Stage 1 (DB + ingestion) ✅
- Stage 2 (dashboard) ✅
- Stage 3 (comparison, similarity, trends, rankings) ✅
- Stage 4 (AI Hebrew queries — claude_client, context_builder, query_engine, insight_generator, /ai/query + /ai/insights endpoints, AIQueryPage) ✅
- Stage 5 (Choropleth map, PDF export, What-If forecasts) ✅ — code complete; map requires `python scripts/seed_coordinates.py` to populate lat/lon

Detailed plans in `.claude/plan/`: `plan.md` (full roadmap), `plan1.md`–`plan4.md`.
