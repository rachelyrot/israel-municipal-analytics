import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models.indicator import Indicator
from app.models.data_point import DataPoint
from app.models.municipality import Municipality

db = SessionLocal()
ind = db.query(Indicator).filter(Indicator.code == 'LAND_TOTAL_AREA').first()

# בדוק עמנואל ספציפית
for name_fragment in ['עמנואל', 'גוש עציון', 'ביתר']:
    m = db.query(Municipality).filter(Municipality.name.contains(name_fragment)).first()
    if not m:
        continue
    rows = (db.query(DataPoint)
            .filter(DataPoint.indicator_id == ind.id, DataPoint.municipality_id == m.id)
            .order_by(DataPoint.year.desc()).limit(5).all())
    print(f"\n{m.name}:")
    for dp in rows:
        print(f"  {dp.year}: {dp.value:.3f} km² | sheet={dp.sheet_name}")

db.close()
