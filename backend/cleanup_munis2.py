# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint

db = SessionLocal()

try:
    # 1. מחיקת 5 ללא נתונים
    to_delete_ids = [774, 775, 739, 779, 742]
    for muni_id in to_delete_ids:
        m = db.query(Municipality).filter(Municipality.id == muni_id).first()
        if m:
            db.delete(m)
            print(f'נמחק: {m.name} (id={m.id})')

    # 2. מחיקת מודיעין-מכבים-רעות ללא כוכבית (id=694, 11 נקודות שכבר מכוסות)
    dup = db.query(Municipality).filter(Municipality.id == 694).first()
    if dup:
        db.query(DataPoint).filter(DataPoint.municipality_id == 694).delete()
        db.delete(dup)
        print(f'נמחק כפיל: {dup.name} (id=694)')

    db.flush()

    # 3. שינוי שם: הסרת כוכביות + הוספה כ-alias
    renames = [
        (469, 'מודיעין-מכבים-רעות*', 'מודיעין-מכבים-רעות'),
        (525, 'בנימינה-גבעת עדה*',    'בנימינה-גבעת עדה'),
        (593, 'סביון*',                'סביון'),
    ]
    for muni_id, old_name, new_name in renames:
        m = db.query(Municipality).filter(Municipality.id == muni_id).first()
        if m:
            aliases = list(m.name_aliases or [])
            if old_name not in aliases:
                aliases.append(old_name)
            m.name = new_name
            m.name_aliases = aliases
            print(f'שם שונה: {old_name!r} -> {new_name!r}')

    db.commit()
    print('\nהכל בוצע בהצלחה.')

except Exception as e:
    db.rollback()
    print(f'שגיאה: {e}')
finally:
    db.close()
