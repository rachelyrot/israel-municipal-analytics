from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage


def build_general_context(db: Session, years: list[int]) -> tuple[str, list[dict]]:
    """
    Context for general questions. Accepts one or more years.
    Builds top-10 rankings per indicator per year — enables year-over-year comparisons.
    """
    from collections import defaultdict

    sources: list[dict] = []
    lines = [f"נתוני רשויות מקומיות בישראל — שנים: {', '.join(str(y) for y in years)}", ""]

    for year in years:
        lines.append(f"{'='*50}")
        lines.append(f"שנת {year}")
        lines.append(f"{'='*50}")

        # National averages
        avg_rows = (
            db.query(NationalAverage, Indicator)
            .join(Indicator, NationalAverage.indicator_id == Indicator.id)
            .filter(NationalAverage.year == year, NationalAverage.avg_value.isnot(None))
            .order_by(Indicator.domain, Indicator.name_he)
            .all()
        )
        if avg_rows:
            lines.append("ממוצעים ארציים:")
            current_domain = None
            for na, ind in avg_rows:
                if ind.domain != current_domain:
                    lines.append(f"[{ind.domain or 'כללי'}]")
                    current_domain = ind.domain
                lines.append(f"  {ind.name_he}: {na.avg_value:,.1f} {ind.unit or ''}")
            lines.append("")

        # Top-N per indicator — limit to 40 most-covered indicators for this year set
        max_indicators = 40 if len(years) > 1 else 60
        top_ind_ids = (
            db.query(DataPoint.indicator_id)
            .filter(DataPoint.year.in_(years), DataPoint.value.isnot(None))
            .group_by(DataPoint.indicator_id)
            .order_by(func.count(DataPoint.id).desc())
            .limit(max_indicators)
            .subquery()
        )
        dp_rows = (
            db.query(DataPoint, Municipality, Indicator)
            .join(Municipality, DataPoint.municipality_id == Municipality.id)
            .join(Indicator, DataPoint.indicator_id == Indicator.id)
            .filter(
                DataPoint.year == year,
                DataPoint.value.isnot(None),
                Indicator.id.in_(top_ind_ids),
            )
            .order_by(Indicator.domain, Indicator.name_he)
            .all()
        )

        by_ind: dict = defaultdict(list)
        ind_meta: dict = {}
        for dp, muni, ind in dp_rows:
            by_ind[ind.id].append((dp.value, muni.name, muni.district))
            ind_meta[ind.id] = ind

        lines.append(f"דירוגים לשנת {year}:")
        for ind_id, entries in by_ind.items():
            ind = ind_meta[ind_id]
            reverse = ind.higher_is_better is not False
            entries.sort(key=lambda x: x[0], reverse=reverse)
            top_n = 5 if len(years) > 1 else 10
            top10 = entries[:top_n]
            lines.append(f"\n{ind.name_he} ({ind.unit or ''}) — {len(entries)} רשויות:")
            for rank, (val, muni_name, district) in enumerate(top10, start=1):
                lines.append(f"  {rank}. {muni_name} ({district or ''}) — {val:,.1f}")
                sources.append({
                    "indicator_code": ind.code,
                    "name_he": ind.name_he,
                    "municipality": muni_name,
                    "value": val,
                    "unit": ind.unit or "",
                    "year": year,
                })
        lines.append("")

    return "\n".join(lines), sources


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


def build_municipality_timeseries_context(db: Session, municipality_id: int) -> tuple[str, list[dict]]:
    """
    Multi-year context for a municipality — all indicators across all available years.
    Used when no specific year is requested.
    """
    muni = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not muni:
        return "רשות לא נמצאה.", []

    rows = (
        db.query(DataPoint, Indicator)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(DataPoint.municipality_id == municipality_id, DataPoint.value.isnot(None))
        .order_by(Indicator.domain, Indicator.name_he, DataPoint.year)
        .all()
    )

    if not rows:
        return f"אין נתונים עבור {muni.name}.", []

    # Group: domain → indicator → {year: value}
    from collections import defaultdict
    by_domain: dict = defaultdict(lambda: defaultdict(dict))
    ind_meta: dict = {}
    for dp, ind in rows:
        by_domain[ind.domain or "כללי"][ind.name_he][dp.year] = dp.value
        ind_meta[ind.name_he] = ind

    lines = [
        f"רשות: {muni.name} | סוג: {muni.municipality_type or 'לא ידוע'} | מחוז: {muni.district or 'לא ידוע'}",
        f"אשכול חברתי-כלכלי: {muni.socioeconomic_cluster or 'לא ידוע'}",
        f"נתונים רב-שנתיים (1999–2024):",
        "",
    ]
    sources = []
    for domain, indicators in by_domain.items():
        lines.append(f"[{domain}]")
        for ind_name, year_vals in indicators.items():
            ind = ind_meta[ind_name]
            sorted_years = sorted(year_vals.items())
            year_str = "  ".join(f"{y}: {v:,.1f}" for y, v in sorted_years)
            lines.append(f"  {ind_name} ({ind.unit or ''}): {year_str}")
            for y, v in sorted_years:
                sources.append({
                    "indicator_code": ind.code,
                    "name_he": ind_name,
                    "value": v,
                    "unit": ind.unit,
                    "year": y,
                    "national_avg": None,
                })
        lines.append("")

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
