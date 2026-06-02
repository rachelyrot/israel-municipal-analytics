from app.database import SessionLocal
from app.models.indicator import Indicator

db = SessionLocal()
ind = db.query(Indicator).filter(Indicator.code == "LAND_TOTAL_AREA").first()
print("Current:", ind.cbs_column_variants)

to_add = "סך הכל שטח שיפוט"
current = list(ind.cbs_column_variants)
if to_add not in current:
    current.append(to_add)
    ind.cbs_column_variants = current
    db.commit()
    print("Added:", to_add)
else:
    print("Already exists")
db.close()
print("Done.")
