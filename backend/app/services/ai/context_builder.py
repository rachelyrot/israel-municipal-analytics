from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage


def build_comparison_context(
    db: Session, municipality_ids: list[int], year: int
) -> tuple[str, list[dict]]:
    """
    בונה טבלה השוואתית: כל שורה = מדד, כל עמודה = רשות + ממוצע ארצי.
    מחזיר (context_text, sources_list).
    """
    munis = db.query(Municipality).filter(Municipality.id.in_(municipality_ids)).all()
    muni_map = {m.id: m for m in munis}

    # שלוף כל data_points לכל הרשויות
    rows = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(
            and_(
                DataPoint.municipality_id.in_(municipality_ids),
                DataPoint.year == year,
            )
        )
        .order_by(Indicator.domain, Indicator.name_he)
        .all()
    )

    # אגד לפי מדד: { indicator_id: { muni_id: value, "ind": Indicator, "na": NationalAverage } }
    by_indicator: dict = {}
    for dp, ind, na in rows:
        if dp.value is None:
            continue
        if ind.id not in by_indicator:
            by_indicator[ind.id] = {"ind": ind, "na": na, "values": {}}
        by_indicator[ind.id]["values"][dp.municipality_id] = dp.value

    if not by_indicator:
        names = ", ".join(m.name for m in munis)
        return f"אין נתוני השוואה עבור {names} לשנת {year}.", []

    # כותרת
    muni_names = [muni_map[mid].name for mid in municipality_ids if mid in muni_map]
    header_info = " | ".join(
        f"{muni_map[mid].name} ({muni_map[mid].municipality_type or ''}, אשכול {muni_map[mid].socioeconomic_cluster or '?'})"
        for mid in municipality_ids if mid in muni_map
    )
    lines = [
        f"השוואת רשויות לשנת {year}: {header_info}",
        "",
        "מדד | " + " | ".join(muni_names) + " | ממוצע ארצי",
        "-" * 80,
    ]

    sources = []
    current_domain = None

    for ind_data in by_indicator.values():
        ind = ind_data["ind"]
        na = ind_data["na"]
        values = ind_data["values"]
        domain = ind.domain or "כללי"
        if domain != current_domain:
            lines.append(f"\n[{domain}]")
            current_domain = domain

        val_strs = []
        for mid in municipality_ids:
            v = values.get(mid)
            val_strs.append(f"{v:,.1f}" if v is not None else "—")

        avg_str = f"{na.avg_value:,.1f}" if na and na.avg_value else "אין נתון"
        lines.append(f"  {ind.name_he} | {' | '.join(val_strs)} | {avg_str} {ind.unit or ''}")

        for mid in municipality_ids:
            if mid in values:
                sources.append({
                    "indicator_code": ind.code,
                    "name_he": ind.name_he,
                    "municipality": muni_map[mid].name if mid in muni_map else str(mid),
                    "value": values[mid],
                    "unit": ind.unit,
                    "year": year,
                    "national_avg": na.avg_value if na else None,
                })

    return "\n".join(lines), sources


def build_municipality_context(db: Session, municipality_id: int, year: int) -> tuple[str, list[dict]]:
    """
    מחזיר (context_text, sources_list).
    context_text — טבלה עברית מובנית לשליחה ל-Claude.
    sources_list — רשימת מקורות לציטוט בתשובה.
    """
    muni = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not muni:
        return "רשות לא נמצאה.", []

    rows = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(
            and_(DataPoint.municipality_id == municipality_id, DataPoint.year == year)
        )
        .order_by(Indicator.domain, Indicator.name_he)
        .all()
    )

    if not rows:
        return f"אין נתונים עבור {muni.name} לשנת {year}.", []

    lines = [
        f"רשות: {muni.name} | שנה: {year} | סוג: {muni.municipality_type or 'לא ידוע'} | מחוז: {muni.district or 'לא ידוע'}",
        f"אשכול חברתי-כלכלי: {muni.socioeconomic_cluster or 'לא ידוע'}",
        "",
        "תחום | מדד | ערך | יחידה | ממוצע ארצי",
        "-" * 60,
    ]

    sources = []
    current_domain = None

    for dp, ind, na in rows:
        if dp.value is None:
            continue
        domain = ind.domain or "כללי"
        if domain != current_domain:
            lines.append(f"\n[{domain}]")
            current_domain = domain
        avg_str = f"{na.avg_value:,.1f}" if na and na.avg_value else "אין נתון"
        lines.append(f"  {ind.name_he} | {dp.value:,.2f} | {ind.unit or ''} | ממוצע ארצי: {avg_str}")
        sources.append({
            "indicator_code": ind.code,
            "name_he": ind.name_he,
            "value": dp.value,
            "unit": ind.unit,
            "year": year,
            "national_avg": na.avg_value if na else None,
        })

    return "\n".join(lines), sources
