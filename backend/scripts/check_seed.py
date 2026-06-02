import json
with open('data/seed/indicators_seed.json', encoding='utf-8') as f:
    data = json.load(f)
print(f'indicators_seed.json: {len(data)} indicators')
for ind in data:
    print(f"  {ind['code']}: {len(ind.get('cbs_column_variants',[]))} variants")
