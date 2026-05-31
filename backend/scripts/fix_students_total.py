# -*- coding: utf-8 -*-
"""
fix_students_total.py
----------------------
EDU_STUDENTS_TOTAL מוצג עם ערכים כ-25 לשנים 2016-2024 —
נתפסה עמודת "ממוצע תלמידים לכיתה" במקום "תלמידים - סה"כ".

הסקריפט:
1. מוחק את הנתונים השגויים (2016-2024, ערך < 100)
2. קולט מחדש את סך-תלמידים הנכון ישירות מקבצי CBS Excel
3. מרענן national_averages

הרצה: python scripts/fix_students_total.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from app.database import SessionLocal
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.municipality import Municipality
from app.services.ingestion.excel_parser import parse_cbs_file
from sqlalchemy import text

UPLOADS = Path(__file__).parent.parent / "data" / "uploads"
FIX_YEARS = range(2016, 2025)


def extract_students_total(year: int) -> dict[str, float]:
    """מחזיר {symbol_cbs: total_students} לשנה — מחפש עמודה שנגמרת ב-'תלמידים | סה"כ'."""
    for ext in (".xlsx", ".xls"):
        fpath = UPLOADS / f"cbs_{year}{ext}"
        if fpath.exists():
            break
    else:
        return {}

    sheets = parse_cbs_file(fpath, year)
    result: dict[str, float] = {}

    for df in sheets.values():
        if "column_header" not in df.columns:
            continue
        # מחפש עמודה שמכילה "תלמידים | סה"כ" (לפעמים יש מספרים אחרי)
        total_col = next(
            (h for h in df["column_header"].unique()
             if 'תלמידים | סה"כ' in str(h)
             and "ממוצע" not in str(h) and "נושר" not in str(h) and "זכאים" not in str(h)),
            None,
        )
        if total_col is None:
            continue
        subset = df[df["column_header"] == total_col][["symbol_cbs", "value"]].dropna()
        for _, row in subset.iterrows():
            sym = str(row["symbol_cbs"])
            if sym not in result and row["value"] > 50:   # אל תתפוס ערכי גודל-כיתה
                result[sym] = row["value"]

    return result


def run():
    db = SessionLocal()
    try:
        ind = db.query(Indicator).filter_by(code="EDU_STUDENTS_TOTAL").first()
        if not ind:
            print("EDU_STUDENTS_TOTAL לא קיים"); return

        munis = {str(m.symbol_cbs): m.id
                 for m in db.query(Municipality).filter(Municipality.symbol_cbs.isnot(None)).all()}

        # שלב 1: מחיקת כל הנתונים לשנים 2016+ (שגויים — גודל-כיתה במקום סך תלמידים)
        deleted = db.execute(text("""
            DELETE FROM data_points
            WHERE indicator_id = :ind_id AND year >= 2016
        """), {"ind_id": ind.id}).rowcount
        db.commit()
        print(f"נמחקו {deleted} רשומות לשנים 2016+")

        # שלב 2: קליטה מחדש מ-Excel
        total_inserted = 0
        affected_years = []
        for year in FIX_YEARS:
            students = extract_students_total(year)
            if not students:
                print(f"{year}: לא נמצא קובץ/עמודה — מדלג")
                continue

            rows_to_insert = [
                {"municipality_id": munis[sym], "indicator_id": ind.id,
                 "year": year, "value": round(val, 1)}
                for sym, val in students.items() if sym in munis
            ]
            if rows_to_insert:
                db.execute(text("""
                    INSERT INTO data_points (municipality_id, indicator_id, year, value)
                    VALUES (:municipality_id, :indicator_id, :year, :value)
                    ON CONFLICT (municipality_id, indicator_id, year) DO UPDATE
                        SET value = EXCLUDED.value
                """), rows_to_insert)
            inserted = len(rows_to_insert)
            db.commit()
            total_inserted += inserted
            affected_years.append(year)
            print(f"{year}: {inserted} רשויות | avg={sum(students.values())/len(students):.0f}")

        # שלב 3: ריענון national_averages
        for year in affected_years:
            db.execute(text("""
                INSERT INTO national_averages
                    (indicator_id, year, avg_value, median_value, percentile_25, percentile_75)
                SELECT :ind_id, :year,
                       AVG(value),
                       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value),
                       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value),
                       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value)
                FROM data_points
                WHERE indicator_id = :ind_id AND year = :year
                ON CONFLICT (indicator_id, year) DO UPDATE SET
                    avg_value     = EXCLUDED.avg_value,
                    median_value  = EXCLUDED.median_value,
                    percentile_25 = EXCLUDED.percentile_25,
                    percentile_75 = EXCLUDED.percentile_75
            """), {"ind_id": ind.id, "year": year})
        db.commit()

        print(f"\nסה\"כ תוקנו {total_inserted} רשומות ב-{len(affected_years)} שנים")

    finally:
        db.close()


if __name__ == "__main__":
    run()
