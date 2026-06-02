# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

targets = ['נחל שורק', 'עמק לוד']

with open('missing_detail.txt', 'w', encoding='utf-8') as f:
    for name in targets:
        f.write(f'=== {name} ===\n')
        # exact match
        m = db.query(Municipality).filter(Municipality.name == name).first()
        if m:
            f.write(f'  בטבלת municipalities: כן (id={m.id}, type={m.municipality_type})\n')
            count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
            f.write(f'  data_points: {count}\n')
        else:
            f.write(f'  בטבלת municipalities: לא נמצא בדיוק\n')
            # search for partial
            similar = db.query(Municipality).filter(Municipality.name.ilike(f'%{name[:4]}%')).all()
            f.write(f'  דומים: {[s.name for s in similar]}\n')
        f.write('\n')

    # Also check all regional councils to see if these should exist
    f.write('=== כל המועצות האזוריות בDB ===\n')
    regionals = db.query(Municipality.name).filter(
        Municipality.municipality_type == 'מועצה אזורית'
    ).order_by(Municipality.name).all()
    for r in regionals:
        f.write(f'  {r[0]}\n')

db.close()
print('Done - see missing_detail.txt')
