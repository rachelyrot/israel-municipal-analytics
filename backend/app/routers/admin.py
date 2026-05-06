from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
from pathlib import Path

from app.database import get_db
from app.services.ingestion import pipeline

router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/ingest")
async def ingest_file(
    file: UploadFile = File(...),
    year: int = Form(...),
    db: Session = Depends(get_db),
):
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    result = pipeline.run(dest, year, db)
    return {
        "filename": file.filename,
        "year": year,
        "rows_inserted": result.rows_inserted,
        "rows_skipped": result.rows_skipped,
        "unmatched_municipalities": result.unmatched_municipalities[:20],
        "unmapped_columns_sample": result.unmapped_columns[:10],
    }
