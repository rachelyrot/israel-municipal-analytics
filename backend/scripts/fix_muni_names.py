# -*- coding: utf-8 -*-
"""One-off script: fix misspelled municipality names in DB."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.indicator import Indicator

db = SessionLocal()
try:
    ind = db.query(Indicator).filter(Indicator.name_he == 'הכנסות מממשרד החינוך').first()
    if ind:
        ind.name_he = 'הכנסות ממשרד החינוך'
        print(f'fixed indicator: {ind.code}')
    else:
        print('indicator not found')
    db.commit()
    print('Done.')
finally:
    db.close()
