import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator


def forecast(
    db: Session,
    municipality_id: int,
    indicator_code: str,
    delta_pct: float = 0.0,
    years_ahead: int = 5,
) -> dict:
    """
    What-If forecast: fits a linear trend on historical data, then projects
    years_ahead into the future with an optional extra delta_pct per year
    applied on top of the trend.

    Returns:
    {
      "indicator": { code, name_he, unit },
      "historical": [{ year, value, is_forecast }],
      "forecast":   [{ year, value, is_forecast }],   # historical + future points
      "base_slope": float,
      "delta_pct":  float,
    }
    """
    rows = (
        db.query(DataPoint, Indicator)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(
            and_(
                DataPoint.municipality_id == municipality_id,
                Indicator.code == indicator_code,
                DataPoint.value.isnot(None),
            )
        )
        .order_by(DataPoint.year)
        .all()
    )

    if len(rows) < 2:
        return {"error": "אין מספיק נתונים היסטוריים (נדרשות לפחות 2 נקודות)"}

    ind = rows[0][1]
    years = np.array([dp.year for dp, _ in rows])
    values = np.array([dp.value for dp, _ in rows])

    slope, intercept = np.polyfit(years, values, 1)
    last_year = int(years[-1])
    last_value = float(values[-1])

    historical = [
        {"year": int(y), "value": float(v), "is_forecast": False}
        for y, v in zip(years, values)
    ]

    delta_per_year = last_value * (delta_pct / 100.0)
    # Start forecast from last observed value (not the regression line),
    # and use the slope as the per-year increment.
    future = [
        {
            "year": last_year + i,
            "value": round(last_value + slope * i + delta_per_year * i, 2),
            "is_forecast": True,
        }
        for i in range(1, years_ahead + 1)
    ]

    return {
        "indicator": {"code": ind.code, "name_he": ind.name_he, "unit": ind.unit},
        "historical": historical,
        "forecast": historical + future,
        "base_slope": round(float(slope), 4),
        "delta_pct": delta_pct,
    }
