# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from pathlib import Path
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from app.services.ingestion.pipeline import run

db = SessionLocal()

# שדות דן קיבלה נתונים שגויים מעמק לוד בכל השנים — ניקוי מוקדם
shdot_dan = db.query(Municipality).filter(Municipality.name == 'שדות דן').first()
if shdot_dan:
    deleted = db.query(DataPoint).filter(DataPoint.municipality_id == shdot_dan.id).delete()
    db.commit()
    print(f'נוקה: שדות דן ({deleted} נקודות מכל השנים)\n')

# כל קבצי ה-CBS לפי שנה
uploads = Path('data/uploads')
files = sorted([
    (int(f.stem.split('_')[1]), f)
    for f in uploads.glob('cbs_*.xl*')
    if f.stem.split('_')[1].isdigit()
])

print(f'קבצים למיון: {len(files)}')
print('-' * 45)

total_inserted = 0
for year, fpath in files:
    result = run(fpath, year, db)
    total_inserted += result.rows_inserted
    print(f'{year}: +{result.rows_inserted:5d} | unmatched={len(result.unmatched_municipalities)}')

print('-' * 45)
print(f'סה"כ נוספו: {total_inserted}')
db.close()
