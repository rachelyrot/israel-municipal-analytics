"""נרמול שמות רשויות — ממפה שם גולמי מ-Excel לרשומה ב-DB."""
import unicodedata
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.municipality import Municipality

_PREFIXES = ["עיריית", "מועצה מקומית", "מועצה אזורית", "מ.מ.", "מ.א.", "עירית"]


def _normalize_str(s: str) -> str:
    s = unicodedata.normalize("NFC", s).strip()
    for p in _PREFIXES:
        if s.startswith(p):
            s = s[len(p):].strip()
    return s


class MunicipalityNormalizer:
    def __init__(self, db: Session):
        self._by_symbol: dict[str, Municipality] = {}
        self._by_name: dict[str, Municipality] = {}
        self._unmatched: list[str] = []

        for m in db.query(Municipality).all():
            if m.symbol_cbs:
                self._by_symbol[m.symbol_cbs] = m
            key = _normalize_str(m.name)
            self._by_name[key] = m
            for alias in (m.name_aliases or []):
                self._by_name[_normalize_str(alias)] = m

    def normalize(self, raw_name: str, symbol_cbs: str | None = None) -> Municipality | None:
        # 1. התאמה לפי סמל CBS (הכי אמין)
        if symbol_cbs:
            sym = str(symbol_cbs).replace(".0", "").lstrip("0") or symbol_cbs
            if sym in self._by_symbol:
                candidate = self._by_symbol[sym]
                # Sanity-check: the CBS uses overlapping code ranges for cities vs.
                # regional councils (e.g. city code 31=אופקים, regional council 31=נחל שורק).
                # Only accept the symbol match when names are reasonably similar.
                name_score = SequenceMatcher(
                    None, _normalize_str(raw_name), _normalize_str(candidate.name)
                ).ratio()
                if name_score >= 0.6:
                    return candidate
                # Fall through to name matching

        # 2. התאמה מדויקת לפי שם
        key = _normalize_str(raw_name)
        if key in self._by_name:
            return self._by_name[key]

        # 3. Fuzzy match
        best_score, best_muni = 0.0, None
        for name_key, muni in self._by_name.items():
            score = SequenceMatcher(None, key, name_key).ratio()
            if score > best_score:
                best_score, best_muni = score, muni

        if best_score >= 0.85:
            return best_muni

        self._unmatched.append(raw_name)
        return None

    def get_unmatched(self) -> list[str]:
        return list(set(self._unmatched))
