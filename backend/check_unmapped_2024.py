# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.services.ingestion.excel_parser import parse_cbs_file
from app.services.ingestion.pipeline import _build_indicator_map
from app.database import SessionLocal
from pathlib import Path

db = SessionLocal()
ind_map = _build_indicator_map(db)

sheets = parse_cbs_file(Path('data/uploads/cbs_2024.xlsx'), 2024)

unmapped = {}
mapped_headers = set()
for sheet_name, df in sheets.items():
    for header in df['column_header'].unique():
        if not header:
            continue
        from app.services.ingestion.pipeline import _find_indicator_id
        ind_id = _find_indicator_id(header, ind_map)
        if ind_id:
            mapped_headers.add(header)
        else:
            unmapped[header] = unmapped.get(header, 0) + 1

with open('unmapped_2024.txt', 'w', encoding='utf-8') as f:
    f.write(f'ממופים: {len(mapped_headers)}\n')
    f.write(f'לא ממופים: {len(unmapped)}\n\n')
    f.write('=== כותרות לא ממופות ===\n')
    for h in sorted(unmapped.keys()):
        f.write(f'  {h}\n')

db.close()
print('Done')
