# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from pathlib import Path
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from app.services.ingestion.pipeline import run
from sqlalchemy import func

db = SessionLocal()

# 1. הסרת נתוני 2015 מרשויות שלא אמורות להיות
wrong_names = [
    'גוש עציון', 'הר חברון', 'מגילות ים המלח', 'מטה בנימין',
    'ערבות הירדן', 'שדות דן', 'שומרון'
]
for name in wrong_names:
    m = db.query(Municipality).filter(Municipality.name == name).first()
    if m:
        deleted = db.query(DataPoint).filter(
            DataPoint.municipality_id == m.id,
            DataPoint.year == 2015
        ).delete()
        print(f'הוסר 2015: {name} ({deleted} נקודות)')

db.commit()

# 2. הרצת ingestion מחדש על 2015
print('\nמריץ ingestion 2015...')
file_path = Path('data/uploads/cbs_2015.xls')
result = run(file_path, 2015, db)
print(f'  inserted: {result.rows_inserted}')
print(f'  skipped:  {result.rows_skipped}')
print(f'  unmatched: {result.unmatched_municipalities[:15]}')

db.close()
