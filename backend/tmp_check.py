import sys
sys.path.insert(0, '.')
from pathlib import Path
from app.services.ingestion.excel_parser import parse_cbs_file

for year in [2005, 2006, 2007, 2008]:
    sheets = parse_cbs_file(Path(f'data/uploads/cbs_{year}.xls'), year)
    print(f'Year {year}: {list(sheets.keys())}')
    for sheet_name, df in sheets.items():
        hits = df[df['column_header'].str.contains('x', na=False)]['column_header'].unique()
        deficit_hits = [h for h in df['column_header'].unique() if 'y' in str(h)]
        print(f'  {sheet_name}: {df.shape[0]} rows, {len(df.column_header.unique())} unique headers')
        break
