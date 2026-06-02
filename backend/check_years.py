import sys
sys.path.insert(0, '.')
from pathlib import Path
from app.services.ingestion.excel_parser import parse_cbs_file

for year in [2005, 2006, 2007, 2008]:
    sheets = parse_cbs_file(Path(f'data/uploads/cbs_{year}.xls'), year)
    print(f'\n=== Year {year} ===')
    for sheet_name, df in sheets.items():
        deficit_cols = [h for h in df['column_header'].unique() if 'גירעון' in str(h) or 'עודף' in str(h)]
        print(f'  Sheet: unique_headers={len(df.column_header.unique())}')
        if deficit_cols:
            for h in deficit_cols[:5]:
                cnt = len(df[df['column_header'] == h])
                vals = df[df['column_header'] == h]['value'].tolist()[:2]
                print(f'    {repr(h)} count={cnt} sample={vals}')
        else:
            print('    NO deficit/surplus columns')
