# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Israeli Municipal Analytics platform — ingests CBS (Central Bureau of Statistics) Excel files (1999–2024) into PostgreSQL and exposes a REST API. Frontend is React + Vite + Tailwind. UI is Hebrew/RTL.

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

# Populate lat/lon from OpenStreetMap (run once after seed; required for map/PDF)
python scripts/seed_coordinates.py

# Re-ingest all CBS files from data/uploads/ (naming: cbs_2020.xlsx)
python scripts/reingest_all.py

# Download + ingest CBS files
python scripts/download_cbs.py --years 2015,2016,2017

# Diagnose ingestion issues (unmapped columns, unmatched municipality names)
python scripts/audit_unmapped.py
python scripts/audit_unmatched.py
python scripts/analyze_mappings.py  # detailed column-to-indicator mapping analysis

# Maintenance / one-off fixes
python scripts/fix_muni_names.py   # fix misspelled municipality names already in DB
python scripts/fix_land_area.py    # patch LAND_TOTAL_AREA indicator if column mis-mapped
python scripts/update_seed.py      # edit indicators_seed.json then run to propagate cbs_column_variants to DB
python scripts/update_seeds.py     # variant — re-seeds all indicator fields (not just variants)

# Run tests (no tests are implemented yet — only __init__.py exists)
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

Tailwind CSS v4 is used via `@tailwindcss/vite` plugin — there is no `tailwind.config.js`.

## Architecture

### Backend (`backend/app/`)

**Data flow:** CBS Excel file → `excel_parser.py` → `normalizer.py` → `pipeline.py` → PostgreSQL

- `main.py` — FastAPI app, CORS for localhost:5173/3000, mounts 7 routers under `/api/v1/`
- `database.py` — SQLAlchemy engine + `get_db()` dependency
- `config.py` — pydantic-settings, reads `backend/.env`; fields: `database_url`, `app_name`, `debug`, `anthropic_api_key`

**4 core tables** (SQLAlchemy models in `app/models/`):
- `municipalities` — 267 Israeli local authorities (255 active in 2016, plus 12 historical/newer); fields include `symbol_cbs` (CBS code), `district`, `region`, `lat`/`lon`, `socioeconomic_cluster` (1–10), `name_aliases` (JSON for fuzzy match)
- `indicators` — ~60 indicators by domain (population/employment/education/welfare/budget/infrastructure/taxes); `code` is the stable key (e.g. `POP_TOTAL`); `cbs_column_variants` (JSON) drives column matching
- `data_points` — time-series (municipality × indicator × year); `ON CONFLICT DO UPDATE` enforces last-write-wins upsert
- `national_averages` — pre-computed avg/median/p25/p75 per (indicator, year), auto-refreshed after each ingestion

**Ingestion service (`services/ingestion/`):**
- `excel_parser.py` — handles `.xls` (xlrd, Windows-1255) and `.xlsx` (openpyxl), skips merged/footnote header rows; cleans values (`-`, `--`, `N/A`, `*` → None)
- `normalizer.py` — resolves raw municipality names: CBS symbol match → exact name → aliases → prefix stripping (`עיריית`, `מועצה מקומית`, etc.) → fuzzy (≥85%)
- `pipeline.py` — `run(file_path, year, db)` returns `IngestionResult`; deduplicates rows from multiple sheets (general/physical sheets preferred over budget/survey); calls `_recompute_national_averages()` after upsert; uploaded files land in `data/uploads/`. After ingestion, `_compute_derived_indicators()` computes 4 derived indicators (stored with `source_file='derived'`): `BUDGET_DEFICIT_PC` (deficit × 1000 / population), `WAGE_GENDER_GAP_PCT` ((men − women) / men × 100), `POP_GENDER_GAP_PCT`, and `HEALTH_CANCER_GENDER_GAP_PCT`. Adding a new derived indicator requires: entry in `indicators_seed.json`, a `_compute_*` function in `pipeline.py`, and a call from `_compute_derived_indicators()`.

**Analytics service (`services/analytics/`):**
- `comparison.py` — multi-municipality comparison: same indicator, range of years, includes national avg series
- `similarity.py` — Euclidean distance on 5 base indicators (POP_TOTAL, EMP_RATE, BUDGET_PER_CAPITA, EDU_BAGRUT_RATE + socioeconomic_cluster), min-max normalized; returns similarity score 0–1. **Note:** the `GET /analytics/similar/{id}` endpoint is **missing** from the analytics router — `api.getSimilar()` calls in `MunicipalityProfile` and `SimilarMunicipalities.jsx` will return 404. The service module is ready; it just needs a router endpoint wired up.
- `trends.py` — linear regression on time-series → slope, direction (`up`/`down`/`stable`), R², Hebrew label
- `rankings.py` — rank municipalities by indicator/year with optional district/type filter; ranking computed in Python after DB query (not a SQL window function)
- `whatif.py` — `forecast(db, muni_id, indicator_code, delta_pct, years_ahead)` → linear trend + optional per-year delta → `GET /analytics/forecast/{id}`

**Export service (`services/export/`):**
- `geojson_builder.py` — builds Point GeoJSON from municipalities with lat/lon; feature properties include `municipality_id`, `municipality_name`, `district`, `municipality_type`, `value`, `national_avg`, `has_data`; metadata includes `indicator_code`, `year`, `count`, `is_percentage`
- `pdf_builder.py` — Hebrew PDF via ReportLab + `arabic-reshaper` + `python-bidi`; font at `services/export/fonts/DavidLibre-Regular.ttf`

**AI service (`services/ai/`):**
- `claude_client.py` — singleton Anthropic client; `chat(question, context, model)` uses `claude-haiku-4-5-20251001` with `cache_control: ephemeral` on the system prompt. Uses `httpx.Client(verify=False)` to bypass SSL inspection (NetFree workaround — do not remove).
- `context_builder.py` — four builder functions:
  - `build_municipality_context(db, muni_id, year)` — single municipality + year: Hebrew table (תחום | מדד | ערך | יחידה | ממוצע ארצי)
  - `build_comparison_context(db, muni_ids, year)` — multi-municipality comparison table with national avg column
  - `build_municipality_timeseries_context(db, muni_id)` — all indicators across all available years for a municipality (used when no year is specified)
  - `build_general_context(db, years)` — national rankings and averages per indicator for one or more years (used when no municipality is specified)
- `insight_generator.py` — Python finds indicators where |deviation from national avg| ≥ 30%, then Claude formulates each as a single Hebrew sentence
- `query_engine.py` — `answer_question(...)` dispatches to one of four modes: general (no municipality → `build_general_context`), municipality+year, municipality+comparison, municipality alone (no year → `build_municipality_timeseries_context`)

**Routers (all mounted under `/api/v1/`; health check at `GET /api/v1/health`):**
- `municipalities.py` — GET `/municipalities`, `/municipalities/search?q=`, `/municipalities/{id}`
- `indicators.py` — GET `/indicators?year=` (optional year filter: only returns indicators that have data points for that year and where municipalities have lat/lon), `/indicators/{code}` (includes `available_years` list)
- `data.py` — GET `/data/points`, `/data/kpis/{id}?year=&domain=` (domain is optional server-side filter; uses SQL `RANK()` window function for national ranking), `/data/timeseries/{id}`, `/data/timeseries/{id}/single`, `/data/compare`
- `admin.py` — POST `/admin/ingest` (multipart: file + year)
- `analytics.py` — GET `/analytics/compare`, `/analytics/trends/{id}`, `/analytics/rankings`, `/analytics/forecast/{id}`
- `ai.py` — POST `/ai/query` (free-form Hebrew question), GET `/ai/insights/{id}` (auto-generated anomaly insights)
- `export.py` — GET `/export/geojson` (choropleth GeoJSON from DB lat/lon), GET `/export/pdf/{id}` (Hebrew PDF with ReportLab)

**Note:** `backend/app/schemas/` and `backend/app/crud/` are empty stubs — routers return raw dicts, not Pydantic response models.

### Database

```
DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal
ANTHROPIC_API_KEY=sk-ant-...
```

`.env` file goes in `backend/`. Single Alembic migration (`initial_schema`) covers all 4 tables. Swagger docs at `http://localhost:8000/docs`.

**Seed data** lives in `backend/data/seed/`: `municipalities_seed.json` (267 entries with aliases) and `indicators_seed.json` (~60 indicators with `cbs_column_variants`). Changes to these files take effect via `python scripts/seed_db.py` (re-seeds) or `python scripts/update_seed.py` (variants only). CBS Excel files land in `backend/data/uploads/` named `cbs_<year>.xlsx` or `cbs_<year>.xls`.

### Frontend (`frontend/src/`)

Routing: `/` → LandingPage; all app pages live under `/app/*`.

Active pages in `App.jsx` (navbar: דשבורד · גרפים · שאל AI):
- **DashboardPage** (`/app/`) — split-pane layout: left panel is `RankingsList`; right panel is `MunicipalityProfile` when a municipality is selected, empty state otherwise. Toolbar at top has year dropdown + `IndicatorSearch` (portal-based dropdown with search, defined inline in `DashboardPage.jsx` — not a separate component file). No map on this page.
- **AnalyticsPage** (`/app/analytics`) — up to 3 municipalities selected via `LocalMunicipalitySelector`; domain tabs show all indicators for the selected domain; `CompareChart` grid shows multi-year time-series for each indicator with national avg overlay
- **AIQueryPage** (`/app/ai`) — single free-form Hebrew text input for general national-level questions; no municipality/year selector; calls `api.aiQuery(question, null, null, sessionId, null)` → `build_general_context` on the backend

`ComparisonPage.jsx`, `MapPage.jsx`, `RankingsPage.jsx`, and `ForecastPage.jsx` exist as files but are not wired into the router or navbar.

Key components:
- `api/client.js` — fetch wrapper for all API calls; base path `/api/v1`; includes `aiQuery()`, `getInsights()`, `getChoroplethGeoJSON()`, `downloadPDF()`, `getForecast()`, `getIndicators(year?)`, `getAllRankings()`, `getSimilar()` (year filter passes through to the backend's lat/lon-aware filter)
- `store/dashboardStore.js` — Zustand: `selectedMunicipality`, `selectedYear` (default 2020), `selectedDomain`, `filterDistrict`, `filterType`, `hideRegional`, `kpis`, `isLoadingKPIs`, `error`; `fetchKPIs()` auto-triggered on municipality/year change (does NOT pass domain to the API — domain filtering is client-side in `KPIGrid`); filter fields used by `RankingsList` and `FilterBar`
- `components/MunicipalityProfile.jsx` — rich right-panel profile: 2-col KPI grid (priority codes first), percentage bars (`PctBar`) with national-avg tick, land-use donut (Recharts PieChart for `LAND_*_PCT` codes), `KPIRadar` (Recharts RadarChart showing value/national_avg ratio for 8 key indicators), `SimilarMunis` inline sub-component, full indicator list. Gender gap indicators (`WAGE_GENDER_GAP_PCT`, `POP_GENDER_GAP_PCT`, `HEALTH_CANCER_GENDER_GAP_PCT`) are in the `GENDER_GAP_CODES` set and rendered as "X% לטובת גברים/נשים" instead of plain percentages.
- `components/RankingsList.jsx` — ranked list of all municipalities for the selected indicator/year; includes search bar and viridis color dots; respects `filterDistrict`/`filterType`/`hideRegional` from the store; shown in DashboardPage left panel always
- `components/FilterBar.jsx` — shared filter bar for type (עירייה/מועצה מקומית/מועצה אזורית), district, hide-regional checkbox, and year; writes to dashboardStore; **not yet wired into any page**
- `components/kpi/KPICard.jsx` — shows value, YoY trend (▲/▼ %), deviation from national avg (%), and national rank if available; click toggles time-series chart
- `components/kpi/KPIGrid.jsx` — responsive grid of KPICards; filters the `kpis` array from the store by `selectedDomain` client-side
- `components/kpi/KPIList.jsx` — compact list alternative to KPIGrid: KPIs grouped by domain with inline `ValueBar`; **not yet wired into any page**
- `components/charts/SemiGauge.jsx` — SVG semi-circular arc gauge for percentage KPIs; **not yet wired into any page**
- `components/charts/SummaryDonut.jsx` — Recharts donut counting KPIs above/around/below national avg; **not yet wired into any page**
- `components/DomainFilter.jsx` — tab-bar to filter KPIs by domain; writes `selectedDomain` to the Zustand store
- `components/charts/CompareChart.jsx` — merges multi-municipality series by year into a single array for Recharts LineChart; used by AnalyticsPage
- `components/maps/ChoroplethMap.jsx` — react-leaflet circle markers, 5 quantile color bins; `onMunicipalityClick` prop receives feature properties including `municipality_id`; **not currently mounted in any active page**
- `components/selectors/MunicipalitySelector.jsx` — Zustand-bound typeahead (300ms debounce); `skipSearch` ref suppresses fetch when municipality is set externally (e.g. ranking row click)
- `components/selectors/LocalMunicipalitySelector.jsx` — controlled (prop-based) variant; takes `value`/`onChange` props and does NOT touch Zustand; use this when multiple selectors appear on the same page (e.g., AnalyticsPage)
- `components/SimilarMunicipalities.jsx` — standalone version; similar functionality also inlined in `MunicipalityProfile` as `SimilarMunis`
- `components/selectors/YearSelector.jsx` — year dropdown (not yet wired into any active page)
- `components/charts/TimeSeriesChart.jsx` — single-municipality time-series chart (used by KPICard on click)
- `components/charts/ForecastChart.jsx` — What-If forecast visualization (used by ForecastPage, which is not yet in the router)

## Implementation Status

- Stage 1 (DB + ingestion) ✅
- Stage 2 (dashboard) ✅
- Stage 3 (comparison, similarity, trends, rankings) ✅
- Stage 4 (AI Hebrew queries — claude_client, context_builder, query_engine, insight_generator, /ai/query + /ai/insights endpoints, AIQueryPage) ✅
- Stage 5 (Choropleth map, PDF export, What-If forecasts) ✅ — map is built but not mounted in any active page; requires `python scripts/seed_coordinates.py` to populate lat/lon
- Stage 6 (Discover / auto-stories) — removed

Detailed plans in `.claude/plan/`: `plan.md` (full roadmap), `plan1.md`–`plan4.md`.
