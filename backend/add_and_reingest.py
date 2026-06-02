# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from pathlib import Path
from app.database import SessionLocal
from app.models import Municipality
from app.services.ingestion.pipeline import run

db = SessionLocal()

# Insert missing municipalities
for entry in [
    {"name": "נחל שורק", "symbol_cbs": None, "municipality_type": "מועצה אזורית",
     "district": "מרכז", "region": "שורקות"},
    {"name": "עמק לוד", "symbol_cbs": None, "municipality_type": "מועצה אזורית",
     "district": "מרכז", "region": "עמק לוד"},
]:
    existing = db.query(Municipality).filter(Municipality.name == entry["name"]).first()
    if existing:
        print(f'כבר קיים: {entry["name"]} (id={existing.id})')
    else:
        m = Municipality(**entry)
        db.add(m)
        db.flush()
        print(f'נוסף: {entry["name"]} (id={m.id})')

db.commit()

# Re-ingest 2016
print('\nמריץ ingestion מחדש על 2016...')
file_path = Path('data/uploads/cbs_2016.xlsx')
result = run(file_path, 2016, db)
print(f'  rows inserted: {result.rows_inserted}')
print(f'  rows skipped:  {result.rows_skipped}')
print(f'  unmatched:     {result.unmatched_municipalities[:10]}')

db.close()
