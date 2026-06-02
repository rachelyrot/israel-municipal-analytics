# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality

db = SessionLocal()

# --- מחיקת 5 רשויות ללא נתונים ---
to_delete_ids = [774, 775, 739, 779, 742]  # גלבוע, גליל עליון, יוקנעם עילית, כנרות, כפר יסיף
for muni_id in to_delete_ids:
    m = db.query(Municipality).filter(Municipality.id == muni_id).first()
    if m:
        print(f'מוחק: {m.name} (id={m.id})')
        db.delete(m)

db.flush()

# --- שינוי שם + alias לשלוש עם כוכבית ---
renames = [
    ('בנימינה-גבעת עדה*', 'בנימינה-גבעת עדה'),
    ('מודיעין-מכבים-רעות*', 'מודיעין-מכבים-רעות'),
    ('סביון*', 'סביון'),
]
for old_name, new_name in renames:
    m = db.query(Municipality).filter(Municipality.name == old_name).first()
    if m:
        aliases = list(m.name_aliases or [])
        if old_name not in aliases:
            aliases.append(old_name)  # שומר את הכוכבית כ-alias לצורך ingestion עתידי
        m.name = new_name
        m.name_aliases = aliases
        print(f'שם שונה: {old_name!r} -> {new_name!r}')

db.commit()
print('\nסיום.')
