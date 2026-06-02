# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

with open('extras_report.txt', 'w', encoding='utf-8') as f:
    # רשויות ללא data_points בכלל
    zero_dp = (
        db.query(Municipality)
        .outerjoin(DataPoint, Municipality.id == DataPoint.municipality_id)
        .group_by(Municipality.id)
        .having(func.count(DataPoint.id) == 0)
        .all()
    )
    f.write(f'=== רשויות ללא נתונים בכלל ({len(zero_dp)}) ===\n')
    for m in sorted(zero_dp, key=lambda x: (x.municipality_type or '', x.name)):
        f.write(f'  id={m.id}, name={m.name!r}, type={m.municipality_type}, sym={m.symbol_cbs!r}, district={m.district}\n')

    f.write(f'\n=== רשויות עם נתונים — לפי מספר שנים ===\n')
    by_years = (
        db.query(Municipality.name, func.count(DataPoint.year.distinct()).label('years'))
        .join(DataPoint, Municipality.id == DataPoint.municipality_id)
        .group_by(Municipality.id, Municipality.name)
        .order_by(func.count(DataPoint.year.distinct()))
        .limit(20)
        .all()
    )
    for name, years in by_years:
        f.write(f'  {name!r}: {years} שנים\n')

db.close()
print('Done')
