import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator

LABELS = {
    "up": "מגמת עלייה",
    "down": "מגמת ירידה",
    "stable": "יציב",
}


def compute_trend(
    db: Session,
    municipality_id: int,
    indicator_code: str,
    year_from: int,
    year_to: int,
) -> dict:
    """
    Performs linear regression on time series data for a municipality + indicator.

    Returns:
    {
      "slope": 2.3,                  # average change per year
      "direction": "up",             # "up" | "down" | "stable" | "insufficient_data"
      "label_he": "מגמת עלייה",
      "r_squared": 0.91,             # fit quality (0–1)
      "pct_change_total": 18.5,      # % change from first to last value
      "data_points_count": 12
    }
    """
    # Fetch the indicator
    indicator = db.query(Indicator).filter(Indicator.code == indicator_code).first()
    if indicator is None:
        return {"direction": "insufficient_data", "label_he": "אין נתונים", "data_points_count": 0}

    # Fetch data points for this municipality + indicator + year range
    rows = (
        db.query(DataPoint)
        .filter(
            and_(
                DataPoint.municipality_id == municipality_id,
                DataPoint.indicator_id == indicator.id,
                DataPoint.year >= year_from,
                DataPoint.year <= year_to,
                DataPoint.value.isnot(None),
            )
        )
        .order_by(DataPoint.year)
        .all()
    )

    # Edge case: fewer than 3 data points
    if len(rows) < 3:
        return {"direction": "insufficient_data", "label_he": "אין נתונים מספיקים", "data_points_count": len(rows)}

    years = np.array([r.year for r in rows], dtype=float)
    values = np.array([r.value for r in rows], dtype=float)

    # Linear regression: polyfit(years, values, degree=1) → [slope, intercept]
    slope, intercept = np.polyfit(years, values, 1)

    # Compute R²
    y_pred = slope * years + intercept
    ss_res = float(np.sum((values - y_pred) ** 2))
    ss_tot = float(np.sum((values - np.mean(values)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Direction logic: if abs(slope / mean_value) < 0.01 → "stable"
    mean_value = float(np.mean(values))
    if mean_value != 0 and abs(slope / mean_value) < 0.01:
        direction = "stable"
    elif slope > 0:
        direction = "up"
    else:
        direction = "down"

    # Percent change total: (last - first) / first * 100
    first_value = float(values[0])
    last_value = float(values[-1])
    pct_change_total = ((last_value - first_value) / first_value * 100) if first_value != 0 else None

    return {
        "slope": round(float(slope), 4),
        "direction": direction,
        "label_he": LABELS[direction],
        "r_squared": round(r_squared, 4),
        "pct_change_total": round(pct_change_total, 2) if pct_change_total is not None else None,
        "data_points_count": len(rows),
    }
