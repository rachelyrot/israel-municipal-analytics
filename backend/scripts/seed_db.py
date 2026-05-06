"""טוען נתוני seed של רשויות ומדדים לתוך ה-DB"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.municipality import Municipality
from app.models.indicator import Indicator


def seed_municipalities(db, seed_file: Path) -> int:
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    data = json.loads(seed_file.read_text(encoding="utf-8"))
    # דדופליקציה לפי symbol_cbs ולפי name
    seen_symbols: set = set()
    seen_names: set = set()
    unique_items = []
    for item in data:
        sym = item.get("symbol_cbs")
        name = item.get("name")
        if sym in seen_symbols or name in seen_names:
            continue
        seen_symbols.add(sym)
        seen_names.add(name)
        unique_items.append(item)

    if not unique_items:
        return 0

    stmt = pg_insert(Municipality).values(unique_items).on_conflict_do_nothing()
    result = db.execute(stmt)
    db.commit()
    return result.rowcount


def seed_indicators(db, seed_file: Path) -> int:
    data = json.loads(seed_file.read_text(encoding="utf-8"))
    count = 0
    for item in data:
        exists = db.query(Indicator).filter_by(code=item["code"]).first()
        if not exists:
            try:
                db.add(Indicator(**item))
                db.flush()
                count += 1
            except Exception:
                db.rollback()
    db.commit()
    return count


def main():
    seed_dir = Path(__file__).parent.parent / "data" / "seed"
    db = SessionLocal()
    try:
        muni_count = seed_municipalities(db, seed_dir / "municipalities_seed.json")
        ind_count = seed_indicators(db, seed_dir / "indicators_seed.json")
        print(f"Seeded: {muni_count} municipalities, {ind_count} indicators")

        total_muni = db.query(Municipality).count()
        total_ind = db.query(Indicator).count()
        print(f"Total in DB: {total_muni} municipalities, {total_ind} indicators")
    finally:
        db.close()


if __name__ == "__main__":
    main()
