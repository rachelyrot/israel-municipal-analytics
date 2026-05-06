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
        mapping[ind.name_he.strip()] = ind.id
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

    # דדופליקציה — שמור רק את הרשומה הראשונה לכל (municipality, indicator, year)
    # הרשומה הראשונה = העמודה הישירה ביותר (לפני עמודות נגזרות)
    deduped: dict[tuple, dict] = {}
    for item in batch:
        key = (item["municipality_id"], item["indicator_id"], item["year"])
        if key not in deduped:
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

    result.unmatched_municipalities = normalizer.get_unmatched()
    result.unmapped_columns = list(unmapped)[:20]
    return result
