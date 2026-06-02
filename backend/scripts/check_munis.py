import json, os, sys
sys.path.insert(0, 'c:/new/backend')

data = json.loads(open('data/seed/municipalities_seed.json', encoding='utf-8').read())
keywords = ['כנרת', 'מכבים', 'צורן', 'שבי ציון', 'שומרון', 'בטוף', 'יבנה', 'שורק', 'אפרים', 'הדסה', 'אבו', 'אפעל', 'עזה', 'הורה', 'קדימה']
for m in data:
    name = m['name']
    for kw in keywords:
        if kw in name:
            print(f"  [{m['symbol_cbs']}] {name} | aliases: {m.get('name_aliases', [])}")
            break
