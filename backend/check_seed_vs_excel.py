# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

with open('seed_vs_excel.txt', 'w', encoding='utf-8') as f:
    # Check what's in DB for נחל שורק
    results = db.query(Municipality).filter(Municipality.name.ilike('%נחל%')).all()
    f.write('=== נחל* בDB ===\n')
    for m in results:
        count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
        f.write(f'  id={m.id}, name={m.name}, symbol_cbs={m.symbol_cbs}, type={m.municipality_type}, data_points={count}\n')

    # Check עמק לוד
    results2 = db.query(Municipality).filter(Municipality.name.ilike('%עמק%')).all()
    f.write('\n=== עמק* בDB ===\n')
    for m in results2:
        count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
        f.write(f'  id={m.id}, name={m.name}, symbol_cbs={m.symbol_cbs}, type={m.municipality_type}, data_points={count}\n')

    # Check by symbol_cbs '31' and '40'
    f.write('\n=== לפי symbol_cbs 31, 40 ===\n')
    for sym in ['31', '40', '0031', '0040']:
        m = db.query(Municipality).filter(Municipality.symbol_cbs == sym).first()
        f.write(f'  symbol={sym}: {m.name if m else "לא קיים"}\n')

db.close()
print('Done')
