"""Pipeline לייבוא קובץ CBS שלם לתוך ה-DB."""
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.indicator import Indicator
from app.models.data_point import DataPoint
from app.models.national_average import NationalAverage
from app.services.ingestion.excel_parser import parse_cbs_file
from app.services.ingestion.normalizer import MunicipalityNormalizer


@dataclass
class IngestionResult:
    rows_inserted: int = 0
    rows_skipped: int = 0
    unmatched_municipalities: list[str] = field(default_factory=list)
    unmapped_columns: list[str] = field(default_factory=list)


def _build_indicator_map(db: Session) -> dict[str, int]:
    """מבנה: {כותרת_עמודה: indicator_id}"""
    mapping: dict[str, int] = {}
    for ind in db.query(Indicator).all():
        for variant in (ind.cbs_column_variants or []):
            mapping[variant.strip()] = ind.id
    return mapping


def _find_indicator_id(header: str, ind_map: dict[str, int]) -> int | None:
    if not header:
        return None
    # 1. התאמה מדויקת
    if header in ind_map:
        return ind_map[header]
    # 2. הכי ספציפית — ה-variant הארוך ביותר שכלול בכותרת
    best_id, best_len = None, 0
    for key, ind_id in ind_map.items():
        if key and len(key) >= 5 and key in header and len(key) > best_len:
            best_id, best_len = ind_id, len(key)
    return best_id


def _compute_derived_indicators(db: Session, year: int):
    """Compute derived indicators: BUDGET_DEFICIT_PC and WAGE_GENDER_GAP_PCT."""
    from sqlalchemy import and_
    _compute_wage_gender_gap(db, year)
    _compute_budget_deficit_pc(db, year)


def _compute_budget_deficit_pc(db: Session, year: int):
    """Compute BUDGET_DEFICIT_PC = BUDGET_DEFICIT (אלפי ₪) * 1000 / POP_TOTAL."""
    from sqlalchemy import and_

    deficit_ind = db.query(Indicator).filter(Indicator.code == "BUDGET_DEFICIT").first()
    pop_ind = db.query(Indicator).filter(Indicator.code == "POP_TOTAL").first()
    pc_ind = db.query(Indicator).filter(Indicator.code == "BUDGET_DEFICIT_PC").first()
    if not (deficit_ind and pop_ind and pc_ind):
        return

    deficit_rows = {
        dp.municipality_id: dp.value
        for dp in db.query(DataPoint).filter(
            and_(DataPoint.indicator_id == deficit_ind.id, DataPoint.year == year),
        ).all()
        if dp.value is not None
    }
    pop_rows = {
        dp.municipality_id: dp.value
        for dp in db.query(DataPoint).filter(
            and_(DataPoint.indicator_id == pop_ind.id, DataPoint.year == year),
        ).all()
        if dp.value is not None and dp.value > 0
    }

    batch = []
    for muni_id, deficit in deficit_rows.items():
        pop = pop_rows.get(muni_id)
        if pop:
            batch.append({
                "municipality_id": muni_id,
                "indicator_id": pc_ind.id,
                "year": year,
                "value": round((deficit * 1000) / pop, 2),
                "source_file": "derived",
                "sheet_name": "derived",
            })

    if batch:
        stmt = pg_insert(DataPoint).values(batch).on_conflict_do_update(
            index_elements=["municipality_id", "indicator_id", "year"],
            set_={"value": pg_insert(DataPoint).excluded.value,
                  "source_file": pg_insert(DataPoint).excluded.source_file},
        )
        db.execute(stmt)
        db.commit()
        _recompute_national_averages(db, pc_ind.id, year)
        db.commit()


def _compute_wage_gender_gap(db: Session, year: int):
    """Compute WAGE_GENDER_GAP_PCT = (WAGE_MEN - WAGE_WOMEN) / WAGE_MEN * 100."""
    from sqlalchemy import and_

    men_ind = db.query(Indicator).filter(Indicator.code == "WAGE_MEN").first()
    women_ind = db.query(Indicator).filter(Indicator.code == "WAGE_WOMEN").first()
    gap_ind = db.query(Indicator).filter(Indicator.code == "WAGE_GENDER_GAP_PCT").first()
    if not (men_ind and women_ind and gap_ind):
        return

    men_rows = {
        dp.municipality_id: dp.value
        for dp in db.query(DataPoint).filter(
            and_(DataPoint.indicator_id == men_ind.id, DataPoint.year == year),
        ).all()
        if dp.value is not None and dp.value > 0
    }
    women_rows = {
        dp.municipality_id: dp.value
        for dp in db.query(DataPoint).filter(
            and_(DataPoint.indicator_id == women_ind.id, DataPoint.year == year),
        ).all()
        if dp.value is not None
    }

    batch = []
    for muni_id, wage_men in men_rows.items():
        wage_women = women_rows.get(muni_id)
        if wage_women is not None:
            gap = round((wage_men - wage_women) / wage_men * 100, 2)
            batch.append({
                "municipality_id": muni_id,
                "indicator_id": gap_ind.id,
                "year": year,
                "value": gap,
                "source_file": "derived",
                "sheet_name": "derived",
            })

    if batch:
        stmt = pg_insert(DataPoint).values(batch).on_conflict_do_update(
            index_elements=["municipality_id", "indicator_id", "year"],
            set_={"value": pg_insert(DataPoint).excluded.value,
                  "source_file": pg_insert(DataPoint).excluded.source_file},
        )
        db.execute(stmt)
        db.commit()
        _recompute_national_averages(db, gap_ind.id, year)
        db.commit()


def _recompute_national_averages(db: Session, indicator_id: int, year: int):
    from sqlalchemy import func
    rows = db.query(DataPoint.value).filter(
        DataPoint.indicator_id == indicator_id,
        DataPoint.year == year,
        DataPoint.value.isnot(None),
    ).all()
    values = [r[0] for r in rows]
    if not values:
        return
    values.sort()
    n = len(values)
    avg = sum(values) / n
    median = values[n // 2]
    p25 = values[int(n * 0.25)]
    p75 = values[int(n * 0.75)]

    stmt = pg_insert(NationalAverage).values(
        indicator_id=indicator_id, year=year,
        avg_value=avg, median_value=median,
        percentile_25=p25, percentile_75=p75,
    ).on_conflict_do_update(
        index_elements=["indicator_id", "year"],
        set_={"avg_value": avg, "median_value": median,
              "percentile_25": p25, "percentile_75": p75},
    )
    db.execute(stmt)


def run(file_path: Path, year: int, db: Session) -> IngestionResult:
    result = IngestionResult()
    normalizer = MunicipalityNormalizer(db)
    ind_map = _build_indicator_map(db)
    unmapped: set[str] = set()
    affected: set[tuple[int, int]] = set()

    sheets = parse_cbs_file(file_path, year)
    if not sheets:
        return result

    batch: list[dict] = []

    for sheet_name, df in sheets.items():
        for _, row in df.iterrows():
            muni = normalizer.normalize(row["name"], row.get("symbol_cbs"))
            if not muni:
                continue

            ind_id = _find_indicator_id(row["column_header"], ind_map)
            if not ind_id:
                unmapped.add(row["column_header"])
                result.rows_skipped += 1
                continue

            batch.append({
                "municipality_id": muni.id,
                "indicator_id": ind_id,
                "year": year,
                "value": row["value"],
                "source_file": file_path.name,
                "sheet_name": sheet_name,
            })
            affected.add((ind_id, year))

    # דדופליקציה — מעדיף גיליונות "כלליים" / "פיזיים" על פני תקציב / סקר / שימושי קרקע
    def _sheet_rank(sheet_name: str) -> int:
        """ציון נמוך = עדיפות גבוהה."""
        s = sheet_name or ""
        if any(k in s for k in ["כלל", "פיזי", "מאפיין", "כללי", "אוכלוסייה"]):
            return 0
        if any(k in s for k in ["תקציב", "ארנונה", "הסקר", "שימושי קרקע", "רווחה"]):
            return 2
        return 1

    deduped: dict[tuple, dict] = {}
    for item in batch:
        key = (item["municipality_id"], item["indicator_id"], item["year"])
        if key not in deduped or _sheet_rank(item["sheet_name"]) < _sheet_rank(deduped[key]["sheet_name"]):
            deduped[key] = item
    batch = list(deduped.values())

    if batch:
        stmt = pg_insert(DataPoint).values(batch).on_conflict_do_update(
            index_elements=["municipality_id", "indicator_id", "year"],
            set_={"value": pg_insert(DataPoint).excluded.value,
                  "source_file": pg_insert(DataPoint).excluded.source_file},
        )
        db.execute(stmt)
        db.commit()
        result.rows_inserted = len(batch)

    for ind_id, yr in affected:
        _recompute_national_averages(db, ind_id, yr)
    db.commit()

    _compute_derived_indicators(db, year)

    result.unmatched_municipalities = normalizer.get_unmatched()
    result.unmapped_columns = list(unmapped)[:20]
    return result
