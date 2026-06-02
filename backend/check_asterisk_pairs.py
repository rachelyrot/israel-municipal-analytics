# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

pairs = [
    ('מודיעין-מכבים-רעות', 'מודיעין-מכבים-רעות*'),
    ('בנימינה-גבעת עדה', 'בנימינה-גבעת עדה*'),
    ('סביון', 'סביון*'),
]

with open('asterisk_pairs.txt', 'w', encoding='utf-8') as f:
    for plain, starred in pairs:
        m_plain = db.query(Municipality).filter(Municipality.name == plain).first()
        m_star  = db.query(Municipality).filter(Municipality.name == starred).first()

        def dp_info(m):
            if not m:
                return 'לא קיים'
            count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
            years = db.query(DataPoint.year.distinct()).filter(DataPoint.municipality_id == m.id).order_by(DataPoint.year).all()
            return f'id={m.id}, dp={count}, שנים={[y[0] for y in years]}'

        f.write(f'{plain}: {dp_info(m_plain)}\n')
        f.write(f'{starred}: {dp_info(m_star)}\n\n')

db.close()
print('Done')
