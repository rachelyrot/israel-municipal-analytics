from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional

from app.database import get_db
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage

router = APIRouter(tags=["data"])


@router.get("/data/points")
def get_data_points(
    municipality_id: int,
    indicator_code: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = (
        db.query(DataPoint, Indicator)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(DataPoint.municipality_id == municipality_id)
    )
    if indicator_code:
        q = q.filter(Indicator.code == indicator_code)
    if year_from:
        q = q.filter(DataPoint.year >= year_from)
    if year_to:
        q = q.filter(DataPoint.year <= year_to)

    return [
        {
            "year": dp.year,
            "value": dp.value,
            "indicator_code": ind.code,
            "indicator_name": ind.name_he,
            "unit": ind.unit,
        }
        for dp, ind in q.order_by(DataPoint.year).all()
    ]


@router.get("/data/kpis/{municipality_id}")
def get_kpis(
    municipality_id: int,
    year: int,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            (NationalAverage.indicator_id == DataPoint.indicator_id) &
            (NationalAverage.year == DataPoint.year),
        )
        .filter(DataPoint.municipality_id == municipality_id, DataPoint.year == year)
    )
    if domain:
        q = q.filter(Indicator.domain == domain)

    # חישוב שינוי YoY
    prev_year = year - 1
    prev_values = {
        dp.indicator_id: dp.value
        for dp in db.query(DataPoint).filter(
            DataPoint.municipality_id == municipality_id,
            DataPoint.year == prev_year,
        ).all()
    }

    # חישוב דירוג ארצי לכל מדד
    rank_subq = (
        db.query(
            DataPoint.indicator_id,
            func.rank().over(
                order_by=DataPoint.value.desc(),
                partition_by=DataPoint.indicator_id,
            ).label("rnk"),
            DataPoint.municipality_id,
        )
        .filter(DataPoint.year == year)
        .subquery()
    )
    ranks = {
        row.indicator_id: row.rnk
        for row in db.query(rank_subq).filter(
            rank_subq.c.municipality_id == municipality_id
        ).all()
    }

    import math

    def safe(v):
        if v is None: return None
        try:
            return None if math.isnan(v) or math.isinf(v) else v
        except (TypeError, ValueError):
            return None

    result = []
    for dp, ind, nat_avg in q.all():
        value = safe(dp.value)
        if value is None:
            continue
        prev_val = prev_values.get(ind.id)
        trend_pct = None
        if prev_val and prev_val != 0:
            try:
                trend_pct = round((value - prev_val) / abs(prev_val) * 100, 1)
            except Exception:
                pass

        result.append({
            "indicator_code": ind.code,
            "name_he": ind.name_he,
            "domain": ind.domain,
            "unit": ind.unit,
            "value": value,
            "national_avg": safe(nat_avg.avg_value) if nat_avg else None,
            "trend_pct": safe(trend_pct),
            "rank_national": ranks.get(ind.id),
            "higher_is_better": ind.higher_is_better,
        })
    return result


@router.get("/data/timeseries/{municipality_id}")
def get_timeseries(
    municipality_id: int,
    indicator_codes: str = Query(..., description="קודים מופרדים בפסיק"),
    year_from: int = 2005,
    year_to: int = 2023,
    db: Session = Depends(get_db),
):
    codes = [c.strip() for c in indicator_codes.split(",")]
    indicators = db.query(Indicator).filter(Indicator.code.in_(codes)).all()
    ind_map = {ind.id: ind for ind in indicators}

    rows = (
        db.query(DataPoint)
        .filter(
            DataPoint.municipality_id == municipality_id,
            DataPoint.indicator_id.in_(ind_map.keys()),
            DataPoint.year.between(year_from, year_to),
        )
        .order_by(DataPoint.year)
        .all()
    )

    # קיבוץ לפי שנה
    by_year: dict = {}
    for dp in rows:
        by_year.setdefault(dp.year, {})[ind_map[dp.indicator_id].code] = dp.value

    # ממוצעים ארציים
    nat_avgs = (
        db.query(NationalAverage)
        .filter(
            NationalAverage.indicator_id.in_(ind_map.keys()),
            NationalAverage.year.between(year_from, year_to),
        )
        .all()
    )
    nat_by_year: dict = {}
    for n in nat_avgs:
        nat_by_year.setdefault(n.year, {})[ind_map[n.indicator_id].code] = n.avg_value

    return {
        "municipality_id": municipality_id,
        "indicators": [{"code": ind.code, "name_he": ind.name_he, "unit": ind.unit} for ind in indicators],
        "data": [
            {"year": yr, "values": by_year.get(yr, {}), "national_avg": nat_by_year.get(yr, {})}
            for yr in sorted(set(list(by_year.keys()) + list(nat_by_year.keys())))
        ],
    }


@router.get("/data/timeseries/{municipality_id}/single")
def get_timeseries_single(
    municipality_id: int,
    indicator_code: str = Query(...),
    year_from: int = 2005,
    year_to: int = 2023,
    db: Session = Depends(get_db),
):
    """מחזיר [{year, value, national_avg}] למדד יחיד — לשימוש בגרף קו."""
    ind = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    if not ind:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Indicator not found")

    rows = (
        db.query(DataPoint)
        .filter(
            DataPoint.municipality_id == municipality_id,
            DataPoint.indicator_id == ind.id,
            DataPoint.year.between(year_from, year_to),
        )
        .order_by(DataPoint.year)
        .all()
    )

    nat_avgs = {
        n.year: n.avg_value
        for n in db.query(NationalAverage)
        .filter(
            NationalAverage.indicator_id == ind.id,
            NationalAverage.year.between(year_from, year_to),
        )
        .all()
    }

    return [
        {"year": dp.year, "value": dp.value, "national_avg": nat_avgs.get(dp.year)}
        for dp in rows
    ]


@router.get("/data/compare")
def compare_municipalities(
    municipality_ids: str = Query(..., description="IDs מופרדים בפסיק"),
    indicator_code: str = Query(...),
    year_from: int = 2010,
    year_to: int = 2016,
    db: Session = Depends(get_db),
):
    ids = [int(i) for i in municipality_ids.split(",")]
    ind = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    if not ind:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Indicator not found")

    rows = (
        db.query(DataPoint, Municipality)
        .join(Municipality, DataPoint.municipality_id == Municipality.id)
        .filter(
            DataPoint.municipality_id.in_(ids),
            DataPoint.indicator_id == ind.id,
            DataPoint.year.between(year_from, year_to),
        )
        .order_by(DataPoint.year)
        .all()
    )

    by_muni: dict = {}
    for dp, m in rows:
        by_muni.setdefault(m.id, {"name": m.name, "data": []})["data"].append(
            {"year": dp.year, "value": dp.value}
        )

    return {
        "indicator": {"code": ind.code, "name_he": ind.name_he, "unit": ind.unit},
        "municipalities": list(by_muni.values()),
    }
