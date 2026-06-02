# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

with open('all_years_coverage.txt', 'w', encoding='utf-8') as f:
    rows = (
        db.query(DataPoint.year, func.count(Municipality.id.distinct()))
        .join(Municipality, Municipality.id == DataPoint.municipality_id)
        .group_by(DataPoint.year)
        .order_by(DataPoint.year)
        .all()
    )
    f.write('שנה | רשויות עם נתונים\n')
    f.write('-' * 25 + '\n')
    for year, count in rows:
        f.write(f'{year}  |  {count}\n')

db.close()
print('Done')
