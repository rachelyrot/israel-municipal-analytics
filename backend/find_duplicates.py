# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import Municipality, DataPoint
from sqlalchemy import func

db = SessionLocal()

all_munis = db.query(Municipality).order_by(Municipality.name).all()

with open('duplicates_report.txt', 'w', encoding='utf-8') as f:
    # 1. כפלויות ברורות — אותו שם בדיוק
    from collections import Counter
    name_counts = Counter(m.name for m in all_munis)
    exact_dups = {n: c for n, c in name_counts.items() if c > 1}
    if exact_dups:
        f.write('=== כפלויות שם מדויק ===\n')
        for name, count in sorted(exact_dups.items()):
            entries = [m for m in all_munis if m.name == name]
            for m in entries:
                dp_count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
                f.write(f'  id={m.id}, name={m.name!r}, symbol={m.symbol_cbs!r}, type={m.municipality_type}, data_points={dp_count}\n')
            f.write('\n')
    else:
        f.write('אין כפלויות שם מדויק\n\n')

    # 2. שמות דומים מאוד (עם/בלי ה, עם/בלי רווח, וריאנטים)
    f.write('=== שמות דומים (וריאנטים) ===\n')
    pairs_seen = set()
    for i, m1 in enumerate(all_munis):
        for m2 in all_munis[i+1:]:
            n1 = m1.name.strip().replace('ה', '', 1) if m1.name.startswith('ה') else m1.name
            n2 = m2.name.strip().replace('ה', '', 1) if m2.name.startswith('ה') else m2.name
            if n1 == n2 or m1.name.replace(' ', '') == m2.name.replace(' ', ''):
                key = (min(m1.id, m2.id), max(m1.id, m2.id))
                if key not in pairs_seen:
                    pairs_seen.add(key)
                    dp1 = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m1.id).scalar()
                    dp2 = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m2.id).scalar()
                    f.write(f'  {m1.name!r} (id={m1.id}, sym={m1.symbol_cbs}, dp={dp1})\n')
                    f.write(f'  {m2.name!r} (id={m2.id}, sym={m2.symbol_cbs}, dp={dp2})\n\n')

    # 3. סמלים כפולים
    f.write('=== סמלי CBS כפולים ===\n')
    sym_counts = Counter(m.symbol_cbs for m in all_munis if m.symbol_cbs)
    dup_syms = {s: c for s, c in sym_counts.items() if c > 1}
    if dup_syms:
        for sym, count in sorted(dup_syms.items()):
            entries = [m for m in all_munis if m.symbol_cbs == sym]
            for m in entries:
                dp_count = db.query(func.count(DataPoint.id)).filter(DataPoint.municipality_id == m.id).scalar()
                f.write(f'  sym={sym!r}: id={m.id}, name={m.name!r}, type={m.municipality_type}, dp={dp_count}\n')
            f.write('\n')
    else:
        f.write('אין כפלויות סמל\n')

db.close()
print('Done')
