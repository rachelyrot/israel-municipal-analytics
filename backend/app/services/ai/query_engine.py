import uuid
from sqlalchemy.orm import Session

from app.services.ai import claude_client, context_builder


def answer_question(
    db: Session,
    question: str,
    municipality_id: int,
    year: int,
    session_id: str | None = None,
    comparison_municipality_ids: list[int] | None = None,
) -> dict:
    """
    Returns:
    {
      "answer": "...",
      "sources": [{ "indicator_code", "name_he", "value", "unit", "year", "national_avg" }],
      "session_id": "uuid",
      "municipality_id": int,
      "year": int,
    }
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    if comparison_municipality_ids:
        all_ids = [municipality_id] + [i for i in comparison_municipality_ids if i != municipality_id]
        context, sources = context_builder.build_comparison_context(db, all_ids, year)
    else:
        context, sources = context_builder.build_municipality_context(db, municipality_id, year)

    if not sources:
        return {
            "answer": f"אין נתונים זמינים לרשות זו לשנת {year}.",
            "sources": [],
            "session_id": session_id,
            "municipality_id": municipality_id,
            "year": year,
        }

    answer = claude_client.chat(question, context)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "municipality_id": municipality_id,
        "year": year,
    }
