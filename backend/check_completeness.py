# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint, Indicator
from sqlalchemy import func

db = SessionLocal()

total_indicators = db.query(func.count(Indicator.id)).scalar()

# ממוצע נקודות לרשות לשנה (לשנים 2012-2023 — שנים "בשלות")
from sqlalchemy import text
row = db.execute(text("""
    SELECT AVG(cnt), MIN(cnt), MAX(cnt) FROM (
        SELECT municipality_id, year, COUNT(*) as cnt
        FROM data_points
        WHERE year BETWEEN 2012 AND 2023
        GROUP BY municipality_id, year
    ) sub
""")).one()
avg_per_muni_year, min_dp, max_dp = row

# רשויות עם מעט נתונים יחסית בשנה מסוימת (פחות מ-20 נקודות)
sparse = (
    db.query(Municipality.name, DataPoint.year, func.count(DataPoint.id).label('cnt'))
    .join(DataPoint, Municipality.id == DataPoint.municipality_id)
    .filter(DataPoint.year.between(2012, 2023))
    .group_by(Municipality.name, DataPoint.year)
    .having(func.count(DataPoint.id) < 20)
    .order_by(DataPoint.year, func.count(DataPoint.id))
    .all()
)

with open('completeness.txt', 'w', encoding='utf-8') as f:
    f.write(f'סה"כ מדדים בDB: {total_indicators}\n')
    f.write(f'ממוצע נקודות לרשות/שנה (2012-2023): {avg_per_muni_year:.1f}\n')
    f.write(f'מינימום: {min_dp} | מקסימום: {max_dp}\n\n')
    f.write(f'רשויות עם פחות מ-20 נקודות בשנה ({len(sparse)}):\n')
    for name, year, cnt in sparse[:30]:
        f.write(f'  {name} | {year} | {cnt} נקודות\n')
    if len(sparse) > 30:
        f.write(f'  ... ועוד {len(sparse)-30}\n')

db.close()
print('Done')
