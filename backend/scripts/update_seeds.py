"""Update indicators (cbs_column_variants) and municipalities (name_aliases + new entries)
from seed JSON files. Uses upsert logic so it can be run repeatedly."""
import sys, json, os
from pathlib import Path

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.indicator import Indicator
from sqlalchemy.dialects.postgresql import insert as pg_insert

db = SessionLocal()
seed_dir = Path(__file__).parent.parent / "data" / "seed"


def update_indicators(db, seed_file: Path):
    data = json.loads(seed_file.read_text(encoding="utf-8"))
    inserted = 0
    updated = 0
    for item in data:
        exists = db.query(Indicator).filter_by(code=item["code"]).first()
        if not exists:
            try:
                db.add(Indicator(**item))
                db.flush()
                inserted += 1
            except Exception as e:
                db.rollback()
                print(f"  ERROR inserting {item['code']}: {e}")
        else:
            # Update cbs_column_variants with new variants
            old_variants = set(exists.cbs_column_variants or [])
            new_variants = set(item.get("cbs_column_variants", []))
            merged = list(old_variants | new_variants)
            if merged != exists.cbs_column_variants:
                exists.cbs_column_variants = merged
                updated += 1
    db.commit()
    return inserted, updated


def update_municipalities(db, seed_file: Path):
    data = json.loads(seed_file.read_text(encoding="utf-8"))
    inserted = 0
    aliases_updated = 0

    # Build a lookup by symbol_cbs
    seen_symbols: set = set()
    seen_names: set = set()

    for item in data:
        sym = item.get("symbol_cbs")
        name = item.get("name")

        # skip dupes within seed
        if sym in seen_symbols or name in seen_names:
            continue
        seen_symbols.add(sym)
        seen_names.add(name)

        exists_by_sym = db.query(Municipality).filter_by(symbol_cbs=sym).first()
        exists_by_name = db.query(Municipality).filter_by(name=name).first()

        if exists_by_sym or exists_by_name:
            target = exists_by_sym or exists_by_name
            # Update aliases
            old_aliases = set(target.name_aliases or [])
            new_aliases = set(item.get("name_aliases", []))
            merged = list(old_aliases | new_aliases)
            if set(merged) != old_aliases:
                target.name_aliases = merged
                aliases_updated += 1
        else:
            try:
                db.add(Municipality(**item))
                db.flush()
                inserted += 1
            except Exception as e:
                db.rollback()
                print(f"  ERROR inserting {name}: {e}")

    db.commit()
    return inserted, aliases_updated


try:
    ind_inserted, ind_updated = update_indicators(db, seed_dir / "indicators_seed.json")
    muni_inserted, muni_aliases = update_municipalities(db, seed_dir / "municipalities_seed.json")

    total_ind = db.query(Indicator).count()
    total_muni = db.query(Municipality).count()

    print(f"Indicators: {ind_inserted} new, {ind_updated} updated (total {total_ind})")
    print(f"Municipalities: {muni_inserted} new, {muni_aliases} aliases updated (total {total_muni})")
finally:
    db.close()
