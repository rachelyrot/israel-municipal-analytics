from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.indicator import Indicator

router = APIRouter(tags=["indicators"])


@router.get("/indicators")
def list_indicators(year: Optional[int] = None, db: Session = Depends(get_db)):
    from app.models.data_point import DataPoint
    from sqlalchemy import exists

    query = db.query(Indicator).order_by(Indicator.domain, Indicator.name_he)

    if year is not None:
        from app.models.municipality import Municipality
        query = query.filter(
            exists().where(
                (DataPoint.indicator_id == Indicator.id)
                & (DataPoint.year == year)
                & (DataPoint.value.isnot(None))
                & (DataPoint.municipality_id == Municipality.id)
                & (Municipality.lat.isnot(None))
            )
        )

    by_domain: dict = {}
    for ind in query.all():
        by_domain.setdefault(ind.domain, []).append({
            "id": ind.id,
            "code": ind.code,
            "name_he": ind.name_he,
            "unit": ind.unit,
            "is_percentage": ind.is_percentage,
            "higher_is_better": ind.higher_is_better,
        })
    return by_domain


@router.get("/indicators/{code}")
def get_indicator(code: str, db: Session = Depends(get_db)):
    from app.models.data_point import DataPoint
    from sqlalchemy import func

    ind = db.query(Indicator).filter(Indicator.code == code).first()
    if not ind:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Indicator not found")

    years = (
        db.query(DataPoint.year)
        .filter(DataPoint.indicator_id == ind.id)
        .distinct()
        .order_by(DataPoint.year)
        .all()
    )
    return {
        "id": ind.id,
        "code": ind.code,
        "name_he": ind.name_he,
        "domain": ind.domain,
        "unit": ind.unit,
        "available_years": [y[0] for y in years],
    }
