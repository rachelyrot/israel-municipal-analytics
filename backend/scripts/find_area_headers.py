import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from app.services.ingestion.excel_parser import parse_cbs_file

for fname in ['cbs_2016.xlsx', 'cbs_2018.xlsx', 'cbs_2020.xlsx']:
    f = Path(f'data/uploads/{fname}')
    if not f.exists():
        continue
    sheets = parse_cbs_file(f, 2020)
    area_headers = set()
    for df in sheets.values():
        if df.empty:
            continue
        for h in df['column_header'].unique():
            if 'שטח' in h and ('שיפוט' in h or 'כולל' in h or 'קמ' in h):
                area_headers.add(h)
    print(f"\n=== {fname} ===")
    for h in sorted(area_headers):
        print(repr(h))
