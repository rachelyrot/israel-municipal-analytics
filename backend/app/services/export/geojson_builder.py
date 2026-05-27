from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage


def build_choropleth_geojson(db: Session, indicator_code: str, year: int) -> dict:
    """
    Builds a GeoJSON FeatureCollection (Point geometry) from municipalities
    that have lat/lon populated, joined with DataPoints for the given indicator+year.
    Returns features with properties: value, municipality_name, symbol_cbs, district.
    """
    rows = (
        db.query(Municipality, DataPoint, NationalAverage)
        .outerjoin(
            DataPoint,
            and_(
                DataPoint.municipality_id == Municipality.id,
                DataPoint.year == year,
            ),
        )
        .outerjoin(
            Indicator,
            DataPoint.indicator_id == Indicator.id,
        )
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(
            Municipality.lat.isnot(None),
            Municipality.lon.isnot(None),
            Indicator.code == indicator_code,
        )
        .all()
    )

    ind_meta = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    is_percentage = bool(ind_meta.is_percentage) if ind_meta else False

    features = []
    for muni, dp, na in rows:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [muni.lon, muni.lat],
            },
            "properties": {
                "municipality_id": muni.id,
                "muni_code": muni.symbol_cbs,
                "municipality_name": muni.name,
                "district": muni.district,
                "municipality_type": muni.municipality_type,
                "value": dp.value if dp else None,
                "national_avg": na.avg_value if na else None,
                "has_data": dp is not None and dp.value is not None,
            },
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "indicator_code": indicator_code,
            "year": year,
            "count": len(features),
            "is_percentage": is_percentage,
        },
        "features": features,
    }
