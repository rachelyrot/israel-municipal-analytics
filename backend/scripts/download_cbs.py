"""
הורדה וייבוא של קבצי הלמ"ס לפי שנים.

שימוש:
    python scripts/download_cbs.py --years 2017,2018,2019,2020,2021,2022,2023
"""
import argparse
import sys
from pathlib import Path

import requests

# הוסף את תיקיית backend ל-path כדי שאפשר לייבא app.*
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.ingestion import pipeline

UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.cbs.gov.il/he/publications/doclib/2019/hamakomiot1999_2017"


def url_for_year(year: int) -> tuple[str, str]:
    """מחזיר (url, שם_קובץ)."""
    ext = "xls" if year <= 2017 else "xlsx"
    return f"{BASE_URL}/{year}.{ext}", f"{year}.{ext}"


def download(year: int) -> Path | None:
    url, filename = url_for_year(year)
    dest = UPLOAD_DIR / filename

    if dest.exists():
        print(f"  [{year}] קובץ קיים: {dest.name} — מדלג על הורדה")
        return dest

    print(f"  [{year}] מוריד {url} ...", end=" ", flush=True)
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"✓ ({len(r.content) // 1024} KB)")
        return dest
    except Exception as e:
        print(f"✗ שגיאה: {e}")
        return None


def ingest(year: int, file_path: Path):
    db = SessionLocal()
    try:
        print(f"  [{year}] מייבא ...", end=" ", flush=True)
        result = pipeline.run(file_path, year, db)
        print(
            f"✓  {result.rows_inserted} שורות | "
            f"דולג: {result.rows_skipped} | "
            f"לא זוהו: {len(result.unmatched_municipalities)} רשויות"
        )
        if result.unmatched_municipalities:
            print(f"         רשויות לא זוהו: {result.unmatched_municipalities[:5]}")
        if result.unmapped_columns:
            print(f"         עמודות לא מופו (דגימה): {result.unmapped_columns[:5]}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="הורדה וייבוא קבצי הלמ\"ס")
    parser.add_argument(
        "--years",
        required=True,
        help="שנים מופרדות בפסיק, לדוגמה: 2017,2018,2019",
    )
    args = parser.parse_args()

    years = [int(y.strip()) for y in args.years.split(",")]
    print(f"\n=== מתחיל עיבוד {len(years)} שנים: {years} ===\n")

    for year in years:
        print(f"--- שנת {year} ---")
        file_path = download(year)
        if file_path:
            ingest(year, file_path)
        print()

    print("=== סיום ===")


if __name__ == "__main__":
    main()
