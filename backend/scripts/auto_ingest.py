# -*- coding: utf-8 -*-
"""
ingest אוטומטי של קבצי CBS שקיימים ב-data/uploads/ אבל טרם נטענו ל-DB.
מופעל ב-Procfile לפני הפעלת השרת.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.services.ingestion import pipeline

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "data" / "uploads"


MIN_MUNICIPALITIES_PER_YEAR = 200  # פחות מזה — נחשב לחלקי ויש לרענן


def years_complete_in_db(db) -> set[int]:
    from sqlalchemy import text
    rows = db.execute(text(
        "SELECT year FROM data_points GROUP BY year HAVING COUNT(DISTINCT municipality_id) >= :min"
    ), {"min": MIN_MUNICIPALITIES_PER_YEAR}).fetchall()
    return {r[0] for r in rows}


def main() -> None:
    # מצא את כל קבצי CBS בתיקייה (cbs_YYYY.xls / cbs_YYYY.xlsx)
    pattern = re.compile(r"cbs_(\d{4})\.xlsx?$")
    files = {
        int(m.group(1)): f
        for f in sorted(UPLOAD_DIR.glob("cbs_*.xls*"))
        if (m := pattern.match(f.name))
    }

    if not files:
        print("[auto_ingest] לא נמצאו קבצי CBS ב-data/uploads/ — דולג.")
        return

    db = SessionLocal()
    try:
        existing = years_complete_in_db(db)
        missing = {y: f for y, f in files.items() if y not in existing}

        if not missing:
            print(f"[auto_ingest] כל {len(files)} השנים כבר קיימות ב-DB — דולג.")
            return

        print(f"[auto_ingest] מייבא {len(missing)} שנים חסרות: {sorted(missing)}")

        for year, path in sorted(missing.items()):
            print(f"  [{year}] מייבא {path.name}...", end=" ", flush=True)
            try:
                result = pipeline.run(path, year, db)
                print(f"✓  {result.rows_inserted} שורות | לא זוהו: {len(result.unmatched_municipalities)} רשויות")
            except Exception as exc:
                print(f"✗ שגיאה: {exc}")

    finally:
        db.close()

    print("[auto_ingest] סיום.")


if __name__ == "__main__":
    main()
