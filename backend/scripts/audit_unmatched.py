"""Audit unmatched municipality names across all CBS files."""
import sys, json, os, re
from pathlib import Path
from collections import Counter

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal'
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.ingestion.excel_parser import parse_cbs_file
from app.services.ingestion.normalizer import MunicipalityNormalizer

unmatched = Counter()
for f in sorted(Path('data/uploads').glob('cbs_*.xls*')):
    year = int(re.search(r'cbs_(\d{4})', f.name).group(1))
    try:
        sheets = parse_cbs_file(f, year)
        db = SessionLocal()
        norm = MunicipalityNormalizer(db)
        db.close()
        for df in sheets.values():
            for name in df['name'].unique():
                sym = df[df['name']==name]['symbol_cbs'].iloc[0]
                if not norm.normalize(name, sym):
                    unmatched[(name, sym)] += 1
    except Exception as e:
        print(f'{f.name}: ERROR {e}')

print(f'Total unique unmatched: {len(unmatched)}')
print('Top 60 unmatched:')
for (name, sym), c in unmatched.most_common(60):
    print(f'  {c:3d}x  [{sym}]  {name}')

# Save full list
result = [{"name": name, "symbol_cbs": sym, "count": c} for (name, sym), c in unmatched.most_common(200)]
with open('data/uploads/unmatched_munis.json', 'w', encoding='utf-8') as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
