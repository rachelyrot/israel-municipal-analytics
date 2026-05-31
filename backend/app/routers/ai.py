import anthropic
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai import query_engine, insight_generator

router = APIRouter(prefix="/ai", tags=["ai"])


class QueryRequest(BaseModel):
    question: str
    municipality_id: Optional[int] = None
    year: Optional[int] = None
    session_id: Optional[str] = None
    comparison_municipality_ids: Optional[list[int]] = None


@router.post("/query")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    שאלה חופשית בעברית, עם רשות ושנה אופציונליים.
    POST /api/v1/ai/query
    Body: { "question": "מה שיעור הבגרות?", "municipality_id": 504, "year": 2022 }
    Body (general): { "question": "מהי הרשות עם הכי הרבה תושבים?" }
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    try:
        return query_engine.answer_question(
            db, req.question, req.municipality_id, req.year,
            req.session_id, req.comparison_municipality_ids
        )
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY חסר או שגוי — הוסף אותו ל-backend/.env")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"שגיאת Anthropic API: {e}")


@router.get("/insights/{municipality_id}")
def insights(municipality_id: int, year: int = 2022, db: Session = Depends(get_db)):
    """
    תובנות אוטומטיות על רשות ושנה.
    GET /api/v1/ai/insights/504?year=2022
    """
    result = insight_generator.generate_insights(db, municipality_id, year)
    return {"municipality_id": municipality_id, "year": year, "insights": result}
