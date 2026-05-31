import re
import uuid
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.services.ai import claude_client, context_builder
from app.models.data_point import DataPoint


def _extract_years(question: str) -> list[int]:
    """Extract all 4-digit years (1999–2024) from the question."""
    matches = re.findall(r'(?<!\d)(199[9]|20[012]\d)(?!\d)', question)
    years = sorted({int(y) for y in matches if 1999 <= int(y) <= 2024})
    return years


def _find_best_year(db: Session, requested: Optional[int]) -> int:
    """
    Return the best available year:
    - If requested year has data → use it
    - Otherwise → most recent year in DB at or before requested (or global max)
    """
    max_year = db.query(func.max(DataPoint.year)).scalar() or 2022
    if requested is None:
        return max_year
    count = db.query(func.count(DataPoint.id)).filter(DataPoint.year == requested).scalar()
    if count:
        return requested
    # Fall back to most recent year ≤ requested
    fallback = db.query(func.max(DataPoint.year)).filter(DataPoint.year <= requested).scalar()
    return fallback or max_year


def answer_question(
    db: Session,
    question: str,
    municipality_id: Optional[int] = None,
    year: Optional[int] = None,
    session_id: Optional[str] = None,
    comparison_municipality_ids: Optional[list] = None,
) -> dict:
    """
    Returns:
    {
      "answer": "...",
      "sources": [...],
      "session_id": "uuid",
      "municipality_id": int | None,
      "year": int | None,
    }
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    effective_year = year or 2022

    # ── General question (no specific municipality) ──
    if municipality_id is None:
        extracted = _extract_years(question)
        # Resolve each requested year to the best available year in DB
        actual_years = []
        for y in extracted:
            actual_years.append(_find_best_year(db, y))
        if not actual_years:
            actual_years = [_find_best_year(db, None)]

        context, sources = context_builder.build_general_context(db, actual_years)
        answer = claude_client.chat(question, context)
        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id,
            "municipality_id": None,
            "year": actual_years[-1],
        }

    # ── Municipality-specific question ──
    if comparison_municipality_ids:
        all_ids = [municipality_id] + [i for i in comparison_municipality_ids if i != municipality_id]
        context, sources = context_builder.build_comparison_context(db, all_ids, effective_year)
    elif year is None:
        # No year specified → multi-year time-series context
        context, sources = context_builder.build_municipality_timeseries_context(db, municipality_id)
    else:
        context, sources = context_builder.build_municipality_context(db, municipality_id, effective_year)

    if not sources:
        return {
            "answer": f"אין נתונים זמינים לרשות זו לשנת {effective_year}.",
            "sources": [],
            "session_id": session_id,
            "municipality_id": municipality_id,
            "year": effective_year,
        }

    answer = claude_client.chat(question, context)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "municipality_id": municipality_id,
        "year": effective_year,
    }
