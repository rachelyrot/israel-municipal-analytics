# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import openpyxl
from app.database import SessionLocal
from app.models import Municipality

db = SessionLocal()

# Load all names from 2016 Excel
wb = openpyxl.load_workbook(r'data/uploads/cbs_2016.xlsx', read_only=True, data_only=True)
ws = wb['נתונים פיזיים ונתוני אוכלוסייה ']
rows = list(ws.iter_rows(values_only=True))
excel_names_2016 = {str(row[0]).strip() for row in rows[5:] if row[0]}
wb.close()

targets = [
    (774, 'גלבוע'),
    (775, 'גליל עליון'),
    (779, 'כנרות'),
    (742, 'כפר יסיף'),
    (739, 'יוקנעם עילית'),
]

with open('zero_dp_check.txt', 'w', encoding='utf-8') as f:
    for muni_id, name in targets:
        m = db.query(Municipality).filter(Municipality.id == muni_id).first()
        in_excel = name in excel_names_2016
        # Check if there's a "ה" variant in DB
        he_variant = db.query(Municipality).filter(Municipality.name == 'ה' + name).first()
        # Check for similar name in DB
        similar = db.query(Municipality).filter(
            Municipality.name.ilike(f'%{name[1:4]}%')
        ).all()
        similar_names = [s.name for s in similar if s.id != muni_id]

        f.write(f'{name} (id={muni_id}, sym={m.symbol_cbs}):\n')
        f.write(f'  באקסל 2016: {"כן" if in_excel else "לא"}\n')
        f.write(f'  וריאנט עם ה: {he_variant.name + " (id=" + str(he_variant.id) + ")" if he_variant else "אין"}\n')
        f.write(f'  דומים בDB: {similar_names[:4]}\n\n')

db.close()
print('Done')
