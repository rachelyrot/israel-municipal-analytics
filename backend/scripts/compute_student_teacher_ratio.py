# -*- coding: utf-8 -*-
"""
compute_student_teacher_ratio.py
---------------------------------
מחשב יחס תלמיד-מורה לשנים 2018–2023 ישירות מקבצי CBS Excel,
בשילוב עם נתוני EDU_TEACHERS שכבר קיימים בDB.

לשנת 2024 כבר קיים הנתון (חושב מ-EDU_STUDENTS_CURRENT).

הרצה: python scripts/compute_student_teacher_ratio.py
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
TARGET_YEARS = range(2018, 2024)   # 2024 כבר מטופל


def extract_students(year: int) -> dict[str, float]:
    """מחזיר {symbol_cbs: total_students} לשנה נתונה."""
    for ext in (".xlsx", ".xls"):
        fpath = UPLOADS / f"cbs_{year}{ext}"
        if fpath.exists():
            break
    else:
        return {}

    sheets = parse_cbs_file(fpath, year)
    students: dict[str, float] = {}

    for df in sheets.values():
        if "column_header" not in df.columns:
            continue
        # מחפשים עמודה שנגמרת ב-"תלמידים | סה"כ"
        total_col = next(
            (h for h in df["column_header"].unique()
             if str(h).endswith('תלמידים | סה"כ')),
            None,
        )
        if total_col is None:
            # fallback: כותרת שמכילה תלמידים וסה"כ אבל לא ממוצע/נושרים
            candidates = [
                h for h in df["column_header"].unique()
                if "תלמידים" in str(h) and 'סה"כ' in str(h)
                and "ממוצע" not in str(h) and "נושר" not in str(h)
                and "זכאים" not in str(h)
            ]
            if not candidates:
                continue
            total_col = candidates[0]

        subset = df[df["column_header"] == total_col][["symbol_cbs", "value"]].dropna()
        for _, row in subset.iterrows():
            sym = str(row["symbol_cbs"])
            if sym not in students:
                students[sym] = row["value"]

    return students


def run():
    db = SessionLocal()
    try:
        ratio_ind = db.query(Indicator).filter_by(code="EDU_STUDENT_TEACHER_RATIO").first()
        teach_ind = db.query(Indicator).filter_by(code="EDU_TEACHERS").first()
        if not ratio_ind or not teach_ind:
            print("מדד חסר ב-DB"); return

        # בנה lookup: symbol_cbs -> municipality_id
        munis = {str(m.symbol_cbs): m.id
                 for m in db.query(Municipality).filter(Municipality.symbol_cbs.isnot(None)).all()}

        total_inserted = 0
        for year in TARGET_YEARS:
            students_by_sym = extract_students(year)
            if not students_by_sym:
                print(f"{year}: לא נמצא קובץ או עמודת תלמידים")
                continue

            # teachers from DB for this year
            teachers_rows = db.execute(text("""
                SELECT m.symbol_cbs, dp.value
                FROM data_points dp
                JOIN municipalities m ON m.id = dp.municipality_id
                WHERE dp.indicator_id = :ind_id AND dp.year = :year AND dp.value > 0
            """), {"ind_id": teach_ind.id, "year": year}).fetchall()

            teachers_by_sym = {str(r.symbol_cbs): r.value for r in teachers_rows}

            inserted = 0
            for sym, students in students_by_sym.items():
                teachers = teachers_by_sym.get(sym)
                if not teachers or students <= 0:
                    continue
                muni_id = munis.get(sym)
                if not muni_id:
                    continue
                ratio = round(students / teachers, 2)
                dp = DataPoint(
                    municipality_id=muni_id,
                    indicator_id=ratio_ind.id,
                    year=year,
                    value=ratio,
                )
                db.merge(dp)
                inserted += 1

            db.commit()
            total_inserted += inserted
            print(f"{year}: {inserted} רשויות | avg_students={sum(students_by_sym.values())/len(students_by_sym):.0f}")

        # ריענון national_averages
        for year in TARGET_YEARS:
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
            """), {"ind_id": ratio_ind.id, "year": year})
        db.commit()

        print(f"\nסה\"כ נוספו: {total_inserted} רשומות")

    finally:
        db.close()


if __name__ == "__main__":
    run()
