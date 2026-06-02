from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage


def compare_municipalities(
    db: Session,
    municipality_ids: list[int],
    indicator_code: str,
    year_from: int,
    year_to: int,
) -> dict:
    """
    Returns comparison data for multiple municipalities on a single indicator over a year range.

    Returns:
    {
      "indicator": { "code": ..., "name_he": ..., "unit": ... },
      "municipalities": [
        { "id": 1, "name": "תל אביב-יפו", "series": [{ "year": 2015, "value": 123.4 }, ...] },
        ...
      ],
      "national_avg": [{ "year": 2015, "avg_value": 100.0 }, ...]
    }
    """
    # Fetch indicator by code
    indicator = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    if indicator is None:
        raise ValueError(f"Indicator '{indicator_code}' not found")

    # Fetch municipalities
    municipalities = (
        db.query(Municipality)
        .filter(Municipality.id.in_(municipality_ids))
        .all()
    )
    muni_map = {m.id: m for m in municipalities}

    # Fetch all data points for these municipalities + indicator + year range
    data_points = (
        db.query(DataPoint)
        .filter(
            and_(
                DataPoint.indicator_id == indicator.id,
                DataPoint.municipality_id.in_(municipality_ids),
                DataPoint.year >= year_from,
                DataPoint.year <= year_to,
            )
        )
        .order_by(DataPoint.municipality_id, DataPoint.year)
        .all()
    )

    # Group data points by municipality_id
    series_by_muni: dict[int, list[dict]] = {mid: [] for mid in municipality_ids}
    for dp in data_points:
        if dp.value is not None:
            series_by_muni[dp.municipality_id].append({"year": dp.year, "value": dp.value})

    municipalities_result = []
    for mid in municipality_ids:
        muni = muni_map.get(mid)
        name = muni.name if muni else str(mid)
        municipalities_result.append({
            "id": mid,
            "name": name,
            "series": sorted(series_by_muni[mid], key=lambda x: x["year"]),
        })

    # Fetch national averages for the indicator + year range
    national_avgs = (
        db.query(NationalAverage)
        .filter(
            and_(
                NationalAverage.indicator_id == indicator.id,
                NationalAverage.year >= year_from,
                NationalAverage.year <= year_to,
            )
        )
        .order_by(NationalAverage.year)
        .all()
    )

    national_avg_result = [
        {"year": na.year, "avg_value": na.avg_value}
        for na in national_avgs
        if na.avg_value is not None
    ]

    # Compute district averages for all distinct districts of the selected municipalities
    districts = list({m.district for m in municipalities if m.district})
    district_avgs_result = []
    if districts:
        district_rows = (
            db.query(
                Municipality.district,
                DataPoint.year,
                func.avg(DataPoint.value).label("avg_value"),
            )
            .join(Municipality, DataPoint.municipality_id == Municipality.id)
            .filter(
                and_(
                    DataPoint.indicator_id == indicator.id,
                    DataPoint.year >= year_from,
                    DataPoint.year <= year_to,
                    Municipality.district.in_(districts),
                    DataPoint.value.isnot(None),
                )
            )
            .group_by(Municipality.district, DataPoint.year)
            .order_by(Municipality.district, DataPoint.year)
            .all()
        )
        by_district: dict[str, list] = defaultdict(list)
        for row in district_rows:
            by_district[row.district].append({"year": row.year, "avg_value": float(row.avg_value)})
        district_avgs_result = [
            {"district": d, "series": by_district[d]}
            for d in districts
            if by_district[d]
        ]

    # Compute type averages for all distinct municipality types of the selected municipalities
    types = list({m.municipality_type for m in municipalities if m.municipality_type})
    type_avgs_result = []
    if types:
        type_rows = (
            db.query(
                Municipality.municipality_type,
                DataPoint.year,
                func.avg(DataPoint.value).label("avg_value"),
            )
            .join(Municipality, DataPoint.municipality_id == Municipality.id)
            .filter(
                and_(
                    DataPoint.indicator_id == indicator.id,
                    DataPoint.year >= year_from,
                    DataPoint.year <= year_to,
                    Municipality.municipality_type.in_(types),
                    DataPoint.value.isnot(None),
                )
            )
            .group_by(Municipality.municipality_type, DataPoint.year)
            .order_by(Municipality.municipality_type, DataPoint.year)
            .all()
        )
        by_type: dict[str, list] = defaultdict(list)
        for row in type_rows:
            by_type[row.municipality_type].append({"year": row.year, "avg_value": float(row.avg_value)})
        type_avgs_result = [
            {"municipality_type": t, "series": by_type[t]}
            for t in types
            if by_type[t]
        ]

    return {
        "indicator": {
            "code": indicator.code,
            "name_he": indicator.name_he,
            "unit": indicator.unit,
        },
        "municipalities": municipalities_result,
        "national_avg": national_avg_result,
        "district_avgs": district_avgs_result,
        "type_avgs": type_avgs_result,
    }
