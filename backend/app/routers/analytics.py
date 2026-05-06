from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics import comparison, trends, rankings

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/compare")
def compare(
    municipality_ids: str = Query(..., description="IDs מופרדים בפסיק, לדוגמה: 1,2,3"),
    indicator_code: str = Query(...),
    year_from: int = 2010,
    year_to: int = 2022,
    db: Session = Depends(get_db),
):
    """
    השוואת רשויות — אותו מדד, כמה רשויות, טווח שנים.
    GET /api/v1/analytics/compare?municipality_ids=1,2&indicator_code=POP_TOTAL&year_from=2015&year_to=2022
    """
    ids = [int(i.strip()) for i in municipality_ids.split(",") if i.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="No municipality_ids provided")
    try:
        return comparison.compare_municipalities(db, ids, indicator_code, year_from, year_to)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/trends/{municipality_id}")
def trend(
    municipality_id: int,
    indicator_code: str = Query(...),
    year_from: int = 2010,
    year_to: int = 2022,
    db: Session = Depends(get_db),
):
    """
    ניתוח מגמה ליניארי עבור רשות ומדד נתונים.
    GET /api/v1/analytics/trends/{municipality_id}?indicator_code=POP_TOTAL&year_from=2010&year_to=2022
    """
    return trends.compute_trend(db, municipality_id, indicator_code, year_from, year_to)


@router.get("/rankings")
def rank(
    indicator_code: str = Query(...),
    year: int = Query(...),
    district: str | None = None,
    municipality_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    דירוג רשויות לפי מדד ושנה, עם סינון לפי מחוז / סוג רשות.
    GET /api/v1/analytics/rankings?indicator_code=POP_TOTAL&year=2022&limit=10
    """
    try:
        return rankings.get_rankings(db, indicator_code, year, district, municipality_type, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
