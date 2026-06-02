# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

with open('verify_result.txt', 'w', encoding='utf-8') as f:
    for name in ['נחל שורק', 'עמק לוד']:
        m = db.query(Municipality).filter(Municipality.name == name).first()
        if not m:
            f.write(f'{name}: לא נמצא!\n')
            continue
        total = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
        by_year = db.query(DataPoint.year, func.count(DataPoint.id)).filter(
            DataPoint.municipality_id == m.id
        ).group_by(DataPoint.year).order_by(DataPoint.year).all()
        f.write(f'{name} (id={m.id}):\n')
        f.write(f'  סה"כ data_points: {total}\n')
        f.write(f'  לפי שנה: {dict(by_year)}\n\n')

db.close()
print('Done')
