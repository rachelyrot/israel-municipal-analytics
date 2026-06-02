# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import DataPoint, Indicator
from sqlalchemy import func, text

db = SessionLocal()

indicators_2024 = db.query(func.count(DataPoint.indicator_id.distinct())).filter(DataPoint.year == 2024).scalar()

avg = db.execute(text("""
    SELECT AVG(cnt) FROM (
        SELECT municipality_id, COUNT(*) as cnt
        FROM data_points WHERE year = 2024
        GROUP BY municipality_id
    ) sub
""")).scalar()

with open('ind_2024.txt', 'w', encoding='utf-8') as f:
    f.write(f'מדדים עם נתונים ב-2024: {indicators_2024}\n')
    f.write(f'ממוצע נקודות לרשות: {avg:.1f}\n')

db.close()
print('Done')
