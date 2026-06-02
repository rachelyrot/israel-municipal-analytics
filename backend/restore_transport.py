import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.indicator import Indicator
from app.models.data_point import DataPoint
from app.models.national_average import NationalAverage

db = SessionLocal()
ind = db.query(Indicator).filter(Indicator.code == 'TRANSPORT_FATALITIES').first()
ind.cbs_column_variants = [
    'הרוגים',
    'תחבורה | הרוגים',
    'תאונות דרכים עם נפגעים סה"כ',
    'תאונות דרכים עם נפגעים - סה"כ',
]
db.commit()
deleted = db.query(DataPoint).filter(DataPoint.indicator_id == ind.id).delete()
db.query(NationalAverage).filter(NationalAverage.indicator_id == ind.id).delete()
db.commit()
print('variants restored:', ind.cbs_column_variants)
print('data_points deleted:', deleted)
db.close()
