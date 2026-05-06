from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator


def get_rankings(
    db: Session,
    indicator_code: str,
    year: int,
    district: str | None = None,
    municipality_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Returns ranked municipalities for a given indicator and year.

    Sort order: DESC if indicator.higher_is_better, else ASC.
    Rank is computed in Python (1-based enumerate) over all matching rows,
    then limit/offset is applied for pagination.

    Returns:
    {
      "indicator": { "code", "name_he", "unit", "higher_is_better" },
      "year": 2022,
      "total": 256,
      "rankings": [
        { "rank": 1, "municipality_id": ..., "name": ..., "district": ...,
          "municipality_type": ..., "value": ... },
        ...
      ]
    }
    """
    # Fetch indicator by code
    indicator = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    if indicator is None:
        raise ValueError(f"Indicator '{indicator_code}' not found")

    # Build base query: JOIN data_points + municipalities, filter by indicator + year
    query = (
        db.query(DataPoint, Municipality)
        .join(Municipality, DataPoint.municipality_id == Municipality.id)
        .filter(
            and_(
                DataPoint.indicator_id == indicator.id,
                DataPoint.year == year,
                DataPoint.value.isnot(None),
            )
        )
    )

    # Optional filters
    if district:
        query = query.filter(Municipality.district == district)
    if municipality_type:
        query = query.filter(Municipality.municipality_type == municipality_type)

    rows = query.all()

    # Sort in Python: DESC if higher_is_better (or None treated as True), else ASC
    reverse = indicator.higher_is_better is not False  # True or None → DESC
    rows.sort(key=lambda r: r[0].value, reverse=reverse)

    # Total count (before pagination)
    total = len(rows)

    # Assign 1-based ranks over the full sorted list
    ranked = []
    for rank, (dp, muni) in enumerate(rows, start=1):
        ranked.append({
            "rank": rank,
            "municipality_id": muni.id,
            "name": muni.name,
            "district": muni.district,
            "municipality_type": muni.municipality_type,
            "value": dp.value,
        })

    # Apply pagination AFTER ranking
    paginated = ranked[offset: offset + limit]

    return {
        "indicator": {
            "code": indicator.code,
            "name_he": indicator.name_he,
            "unit": indicator.unit,
            "higher_is_better": indicator.higher_is_better,
        },
        "year": year,
        "total": total,
        "rankings": paginated,
    }
