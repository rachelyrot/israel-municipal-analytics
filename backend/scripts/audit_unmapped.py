"""Audit unmapped column headers across all CBS files."""
import sys, json, os, re
from pathlib import Path
from collections import Counter

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal'
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.ingestion.excel_parser import parse_cbs_file
from app.services.ingestion.pipeline import _build_indicator_map, _find_indicator_id

db = SessionLocal()
ind_map = _build_indicator_map(db)
db.close()

print(f"Indicator map has {len(ind_map)} entries")

unmapped = Counter()
for f in sorted(Path('data/uploads').glob('cbs_*.xls*')):
    year = int(re.search(r'cbs_(\d{4})', f.name).group(1))
    try:
        sheets = parse_cbs_file(f, year)
        for df in sheets.values():
            for header in df['column_header'].unique():
                if not _find_indicator_id(header, ind_map):
                    unmapped[header] += 1
        print(f"{f.name}: {sum(len(df) for df in sheets.values())} rows, {len(sheets)} sheets")
    except Exception as e:
        print(f'{f.name}: ERROR {e}')

with open('data/uploads/unmapped_columns.json', 'w', encoding='utf-8') as fh:
    json.dump(unmapped.most_common(200), fh, ensure_ascii=False, indent=2)
print(f'\nTotal unique unmapped headers: {len(unmapped)}')
print('Top 50:')
for h, c in unmapped.most_common(50):
    print(f'  {c:3d}x  {h[:80]}')
