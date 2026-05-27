import re
import math
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.models.national_average import NationalAverage
from app.services.ai.claude_client import get_client

# In-memory cache keyed by (year, count)
_cache: dict = {}


def find_stories(db: Session, year: int, count: int = 15) -> list[dict]:
    cache_key = (year, count)
    if cache_key in _cache:
        return _cache[cache_key]

    # All (municipality, data_point, indicator, national_avg) for this year
    rows = (
        db.query(Municipality, DataPoint, Indicator, NationalAverage)
        .join(DataPoint, DataPoint.municipality_id == Municipality.id)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(DataPoint.year == year)
        .all()
    )

    # Population per municipality for context
    pop_rows = (
        db.query(DataPoint.municipality_id, DataPoint.value)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .filter(Indicator.code == "POP_TOTAL", DataPoint.year == year)
        .all()
    )
    pop_by_muni = {r.municipality_id: r.value for r in pop_rows}

    candidates = []
    for muni, dp, ind, na in rows:
        if dp.value is None or na is None or na.avg_value is None or na.avg_value == 0:
            continue
        if math.isnan(dp.value) or math.isnan(na.avg_value):
            continue
        deviation_pct = (dp.value - na.avg_value) / na.avg_value * 100
        if math.isnan(deviation_pct) or abs(deviation_pct) < 60:
            continue

        # Bonus for surprising cluster/indicator combinations:
        # poor city excelling at a "good" metric, or rich city doing poorly
        cluster = muni.socioeconomic_cluster or 5
        surprise_bonus = 0.0
        if ind.higher_is_better is True:
            if deviation_pct > 0 and cluster <= 4:
                surprise_bonus = (5 - cluster) * 0.12
            elif deviation_pct < 0 and cluster >= 7:
                surprise_bonus = (cluster - 6) * 0.12

        interest_score = abs(deviation_pct) * (1 + surprise_bonus)
        population = pop_by_muni.get(muni.id)

        candidates.append({
            "municipality_id": muni.id,
            "municipality_name": muni.name,
            "municipality_type": muni.municipality_type or "",
            "socioeconomic_cluster": cluster,
            "district": muni.district or "",
            "population": int(population) if population else None,
            "indicator_code": ind.code,
            "indicator_name_he": ind.name_he,
            "domain": ind.domain,
            "unit": ind.unit or "",
            "value": round(dp.value, 1),
            "national_avg": round(na.avg_value, 1),
            "deviation_pct": round(deviation_pct, 1),
            "interest_score": round(interest_score, 2),
            "narrative": "",
        })

    candidates.sort(key=lambda x: x["interest_score"], reverse=True)

    # Max 2 stories per municipality to keep variety
    muni_counts: dict[int, int] = {}
    top_stories: list[dict] = []
    for c in candidates:
        mid = c["municipality_id"]
        muni_counts[mid] = muni_counts.get(mid, 0) + 1
        if muni_counts[mid] <= 2:
            top_stories.append(c)
        if len(top_stories) >= count:
            break

    if not top_stories:
        return []

    narratives = _generate_narratives(top_stories, year)
    for story, narrative in zip(top_stories, narratives):
        story["narrative"] = narrative

    _cache[cache_key] = top_stories
    return top_stories


def _generate_narratives(stories: list[dict], year: int) -> list[str]:
    lines = []
    for i, s in enumerate(stories, 1):
        direction = "גבוה" if s["deviation_pct"] > 0 else "נמוך"
        pop_str = f", {s['population']:,} תושבים" if s["population"] else ""
        lines.append(
            f"{i}. {s['municipality_name']} (אשכול {s['socioeconomic_cluster']}{pop_str}) — "
            f"{s['indicator_name_he']}: {s['value']:,.1f} {s['unit']} — "
            f"{abs(s['deviation_pct']):.0f}% {direction} מהממוצע הארצי ({s['national_avg']:,.1f})"
        )

    prompt = (
        f"לכל אחד מהממצאים הבאים על רשויות מקומיות בישראל לשנת {year}, "
        "כתוב משפט אחד קצר ומעניין בעברית — כמו כותרת בעיתון נתונים. "
        "ניתן להוסיף הקשר כללי ידוע על הרשות אם רלוונטי. "
        "ענה ברשימה ממוספרת בדיוק באותו סדר:\n\n"
        + "\n".join(lines)
    )

    response = get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system="אתה עיתונאי נתונים ישראלי. כתוב משפטים קצרים, עובדתיים ומעניינים בעברית.",
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text

    result = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\d+[\.\)]\s*", "", line)
        if line:
            result.append(line)

    while len(result) < len(stories):
        result.append("")

    return result[: len(stories)]
