# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Israeli Municipal Analytics platform — ingests CBS (Central Bureau of Statistics) Excel files (1999–2023) into PostgreSQL and exposes a REST API. Frontend is React + Vite + Tailwind. UI is Hebrew/RTL.

## Backend Commands

All backend commands run from `c:\new\backend\` with the venv active:

```bash
# Activate venv (Windows)
c:\new\venv\Scripts\activate

# Run dev server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "description"

# Seed DB (municipalities + indicators)
python scripts/seed_db.py

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

> **Known issue:** `vite.config.js` proxies `/api` to `http://localhost:8001` — should be `8000`. Fix before testing the dev frontend against the backend.

## Architecture

### Backend (`backend/app/`)

**Data flow:** CBS Excel file → `excel_parser.py` → `normalizer.py` → `pipeline.py` → PostgreSQL

- `main.py` — FastAPI app, CORS for localhost:5173/3000, mounts 4 routers under `/api/v1/`
- `database.py` — SQLAlchemy engine + `get_db()` dependency
- `config.py` — pydantic-settings, reads `.env`

**4 core tables:**
- `municipalities` — 256 Israeli local authorities, each with `symbol_cbs` (CBS code), `name_aliases` (JSON for fuzzy match)
- `indicators` — ~40 indicators by domain (population/employment/education/welfare/budget/infrastructure/taxes), each with `cbs_column_variants` (JSON) for column matching
- `data_points` — time-series (municipality × indicator × year), unique constraint enforces last-write-wins via `ON CONFLICT DO UPDATE`
- `national_averages` — pre-computed avg/median/percentiles per (indicator, year), auto-refreshed on each ingestion

**Ingestion service (`services/ingestion/`):**
- `excel_parser.py` — handles `.xls` (xlrd, Windows-1255) and `.xlsx` (openpyxl), skips merged/footnote header rows; cleans values (`-`, `--`, `N/A`, `*` → None)
- `normalizer.py` — resolves raw municipality names: CBS symbol match → exact name → aliases → prefix stripping (`עיריית`, `מועצה מקומית`, etc.) → fuzzy (≥85%)
- `pipeline.py` — `run(file_path, year, db)` returns `IngestionResult`; calls `_recompute_national_averages()` after upsert; uploaded files land in `data/uploads/`

**Routers:**
- `municipalities.py` — GET `/municipalities`, `/municipalities/search?q=`, `/municipalities/{id}`
- `indicators.py` — GET `/indicators`, `/indicators/{code}`
- `data.py` — GET `/data/points`, `/data/kpis/{id}`, `/data/timeseries/{id}`, `/data/timeseries/{id}/single`, `/data/compare`
- `admin.py` — POST `/admin/ingest` (multipart: file + year)

### Database

```
DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal
```

Single Alembic migration (`initial_schema`) covers all 4 tables.

### Frontend (`frontend/src/`)

Stage 2 dashboard is complete:

- `api/client.js` — fetch wrapper (`searchMunicipalities`, `getKPIs`, `getTimeSeries`)
- `store/dashboardStore.js` — Zustand: selectedMunicipality, selectedYear, selectedDomain, kpis; `fetchKPIs()` auto-triggered on selection change
- `components/selectors/` — MunicipalitySelector (debounced autocomplete 300ms), YearSelector
- `components/DomainFilter.jsx` — 8 buttons (All + 7 domains), active state
- `components/kpi/` — KPICard (value + trend % + vs national avg + rank), KPIGrid (2/3/4-col responsive)
- `components/charts/` — TimeSeriesChart (Recharts: municipality solid line + national avg dashed)
- `pages/DashboardPage.jsx` — assembles all components; Hebrew RTL layout

## Implementation Plan

Detailed plans in `.claude/plan/`:
- `plan.md` — full 5-stage roadmap
- `plan1.md` — Stage 1 (DB + ingestion) ✅ complete
- `plan2.md` — Stage 2 (dashboard) ✅ complete
- Stage 3+ — comparison views, map (Leaflet), leaderboards, export, deploy
