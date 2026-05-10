from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage
from app.services.ai import claude_client


def generate_insights(db: Session, municipality_id: int, year: int) -> list[str]:
    """
    מחזיר רשימה של עד 4 תובנות עבריות על הרשות.
    Python מזהה חריגות (>30% מהממוצע הארצי), Claude מנסח בלבד.
    """
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
        .all()
    )

    findings = []
    for dp, ind, na in rows:
        if dp.value is None or na is None or na.avg_value is None or na.avg_value == 0:
            continue
        deviation_pct = (dp.value - na.avg_value) / na.avg_value * 100
        if abs(deviation_pct) >= 30:
            direction = "גבוה" if deviation_pct > 0 else "נמוך"
            findings.append(
                f"{ind.name_he}: {dp.value:,.1f} {ind.unit or ''} — "
                f"{abs(deviation_pct):.0f}% {direction} מהממוצע הארצי ({na.avg_value:,.1f})"
            )

    if not findings:
        return []

    findings_text = "\n".join(f"- {f}" for f in findings[:6])
    prompt = (
        f"הנה ממצאים סטטיסטיים על רשות מקומית לשנת {year}:\n"
        f"{findings_text}\n\n"
        "נסח כל ממצא כמשפט עברי קצר ובהיר (משפט אחד לממצא). "
        "אל תוסיף מידע שלא מופיע כאן."
    )

    raw = claude_client.chat(prompt, findings_text)
    insights = [line.lstrip("•-– ").strip() for line in raw.splitlines() if line.strip()]
    return insights[:4]
