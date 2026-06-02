# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import openpyxl
from app.database import SessionLocal
from app.models import Municipality

db = SessionLocal()

wb = openpyxl.load_workbook(r'data/uploads/cbs_2016.xlsx', read_only=True, data_only=True)
ws = wb['נתונים פיזיים ונתוני אוכלוסייה ']
rows = list(ws.iter_rows(values_only=True))

# Find header row (row 3 = index 3)
# Build excel symbol -> name map
excel_map = {}
for row in rows[5:]:  # data starts at row 5
    if row[0] and row[1]:
        name = str(row[0]).strip()
        sym = str(row[1]).strip()
        excel_map[sym] = name

with open('symbol_check.txt', 'w', encoding='utf-8') as f:
    # Check short symbols (1-3 digits) in Excel
    f.write('=== סמלים קצרים באקסל (1-3 ספרות) ===\n')
    for sym, name in sorted(excel_map.items(), key=lambda x: len(x[0])):
        if len(sym) <= 3:
            db_muni = db.query(Municipality).filter(Municipality.symbol_cbs == sym).first()
            db_muni_padded = db.query(Municipality).filter(Municipality.symbol_cbs == sym.zfill(4)).first()
            f.write(f'  Excel: sym={sym!r}, name={name}\n')
            f.write(f'    DB exact match: {db_muni.name if db_muni else "—"}\n')
            f.write(f'    DB padded({sym.zfill(4)}): {db_muni_padded.name if db_muni_padded else "—"}\n')

    # Check אופקים specifically
    f.write('\n=== אופקים ===\n')
    m = db.query(Municipality).filter(Municipality.name == 'אופקים').first()
    if m:
        f.write(f'  DB: symbol_cbs={m.symbol_cbs!r}\n')
    f.write(f'  Excel sym for אופקים: {[s for s, n in excel_map.items() if n == "אופקים"]}\n')

wb.close()
db.close()
print('Done')
