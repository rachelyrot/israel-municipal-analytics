from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.municipality import Municipality

router = APIRouter(tags=["municipalities"])


@router.get("/municipalities")
def list_municipalities(db: Session = Depends(get_db)):
    munis = db.query(Municipality).order_by(Municipality.name).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "symbol_cbs": m.symbol_cbs,
            "municipality_type": m.municipality_type,
            "district": m.district,
            "socioeconomic_cluster": m.socioeconomic_cluster,
        }
        for m in munis
    ]


@router.get("/municipalities/search")
def search_municipalities(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    munis = (
        db.query(Municipality)
        .filter(Municipality.name.ilike(f"%{q}%"))
        .order_by(Municipality.name)
        .limit(20)
        .all()
    )
    return [{"id": m.id, "name": m.name, "district": m.district, "municipality_type": m.municipality_type} for m in munis]


@router.get("/municipalities/{municipality_id}")
def get_municipality(municipality_id: int, db: Session = Depends(get_db)):
    from app.models.data_point import DataPoint
    from sqlalchemy import func

    m = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not m:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Municipality not found")

    years = (
        db.query(DataPoint.year)
        .filter(DataPoint.municipality_id == municipality_id)
        .distinct()
        .order_by(DataPoint.year)
        .all()
    )
    return {
        "id": m.id,
        "name": m.name,
        "symbol_cbs": m.symbol_cbs,
        "municipality_type": m.municipality_type,
        "district": m.district,
        "region": m.region,
        "socioeconomic_cluster": m.socioeconomic_cluster,
        "lat": m.lat,
        "lon": m.lon,
        "available_years": [y[0] for y in years],
    }
