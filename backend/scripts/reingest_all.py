"""
מריץ את ה-pipeline מחדש על כל קבצי CBS שקיימים ב-data/uploads/.
"""
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.ingestion import pipeline

UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"


def main():
    files = sorted(
        [f for f in UPLOAD_DIR.glob("cbs_*.xls*") if f.suffix in (".xls", ".xlsx")],
        key=lambda f: f.name,
    )

    if not files:
        print("לא נמצאו קבצים ב-data/uploads/")
        return

    print(f"נמצאו {len(files)} קבצים\n")

    total_inserted = 0
    for f in files:
        match = re.search(r"cbs_(\d{4})", f.name)
        if not match:
            continue
        year = int(match.group(1))

        print(f"[{year}] {f.name} ...", end=" ", flush=True)
        db = SessionLocal()
        try:
            result = pipeline.run(f, year, db)
            total_inserted += result.rows_inserted
            print(
                f"✓  {result.rows_inserted:,} שורות | "
                f"דולג: {result.rows_skipped:,} | "
                f"לא זוהו: {len(result.unmatched_municipalities)} רשויות"
            )
        except Exception as e:
            print(f"✗ שגיאה: {e}")
        finally:
            db.close()

    print(f"\n=== סה\"כ: {total_inserted:,} שורות יובאו ===")


if __name__ == "__main__":
    main()
