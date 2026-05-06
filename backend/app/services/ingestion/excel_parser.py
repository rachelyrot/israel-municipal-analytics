"""פענוח קבצי Excel של הלמ"ס — רשויות מקומיות בישראל.

מבנה קבצי הלמ"ס (2003+):
  שורה 1-3: כותרות וקטגוריות (ממוזגות)
  שורה 4:   כותרות עמודות ראשיות
  שורות 5-8: סיכומים (כלל ארצי / עיריות / מקומיות / אזוריות) — לדלג
  שורה 9+:  נתוני רשויות בודדות
"""
from pathlib import Path
from typing import Any

import pandas as pd
import xlrd
import openpyxl


# --- נרמול יחידות ---

def _scale_value(header: str, value: float | None) -> float | None:
    """כופל ×1000 כשהכותרת אומרת '(אלפים)' — למניעת חוסר עקביות בין שנים.
    לא נוגע ב'אלפי ₪' או 'אלפי מ"ק' כי המדדים האלה מוגדרים ביחידות אלפים."""
    if value is None or not header:
        return value
    h = header.replace('"', '"')
    if 'אלפים' in h and 'אלפי ₪' not in h and 'אלפי מ' not in h:
        return value * 1000
    return value


# --- ניקוי ערכים ---

def _clean_value(val: Any) -> float | None:
    if val is None:
        return None
    s = str(val).strip()
    if s in ("", "-", "--", "...", "N/A", "n/a", "*", "**", "x", "X", "nan", "None"):
        return None
    s = s.replace(",", "").replace(" ", "").replace("\xa0", "")
    try:
        return float(s)
    except ValueError:
        return None


def _clean_text(val: Any) -> str:
    if not val or str(val).strip() in ("", "nan", "None"):
        return ""
    return str(val).strip().replace("\n", " ").replace("  ", " ")


# --- בניית כותרות מורכבות ---

SKIP_ROW_NAMES = {
    "כלל ארצי", "עיריות", "מועצות מקומיות", "מועצות אזוריות",
    "עיריות סך הכל", "מועצות מקומיות סך הכל", "מועצות אזוריות סך הכל",
    "סך הכל", "ממוצע", "סך הכל בני 20 ומעלה", "סך הכל ארצי",
    "סך הכל בערים המונות", "ערים המונות 100,000",
}


def _is_summary_row(name: str) -> bool:
    if not name:
        return True
    for skip in SKIP_ROW_NAMES:
        if name.startswith(skip) or skip in name:
            return True
    return False


def _build_headers(all_rows: list[list], header_row_idx: int) -> list[str]:
    """בונה כותרות מורכבות על ידי חיבור שורות 1..header_row_idx."""
    n_cols = max((len(r) for r in all_rows[:header_row_idx + 1]), default=0)
    headers = []

    for col in range(n_cols):
        parts = []
        for row in all_rows[:header_row_idx + 1]:
            val = row[col] if col < len(row) else None
            text = _clean_text(val)
            if text and text not in parts and len(text) > 1:
                parts.append(text)
        # הכותרת הספציפית ביותר היא האחרונה
        headers.append(" | ".join(parts))

    return headers


def _find_header_row(all_rows: list[list]) -> int:
    """מוצא את שורת הכותרות הראשית (מכילה 'שם הרשות' או 'סמל הרשות')."""
    for i, row in enumerate(all_rows[:8]):
        row_text = " ".join(_clean_text(c) for c in row if c)
        if "שם הרשות" in row_text or "שם  הרשות" in row_text:
            return i
    # fallback: השורה עם הכי הרבה תאים לא ריקים
    counts = [sum(1 for c in r if c and str(c).strip() not in ("", "nan")) for r in all_rows[:6]]
    return counts.index(max(counts)) if counts else 0


def _find_name_symbol_cols(headers: list[str]) -> tuple[int, int]:
    """מאתר עמודות שם ומספר הרשות."""
    name_col, sym_col = 0, 1
    for i, h in enumerate(headers):
        if "שם" in h and "רשות" in h:
            name_col = i
        if "סמל" in h and ("רשות" in h or "ישוב" in h):
            sym_col = i
    return name_col, sym_col


def _is_valid_symbol(val: Any) -> bool:
    if val is None:
        return False
    s = str(val).strip().replace(".0", "").lstrip("0") or "0"
    return s.isdigit() and 1 <= int(s) <= 99999


def _normalize_symbol(val: Any) -> str:
    s = str(val).strip().replace(".0", "")
    try:
        return str(int(float(s)))
    except (ValueError, TypeError):
        return s.lstrip("0") or s


# --- זיהוי מבנה ---

def _is_transposed(all_rows: list[list]) -> bool:
    """בודק אם הגיליון במבנה הפוך (שורות=מדדים, עמודות=רשויות).
    סימן מובהק: עמודה 0 = 'כללי' ועמודה 1 = 'שם הרשות' / 'סמל הרשות' באחת מ-5 השורות הראשונות.
    """
    for row in all_rows[:5]:
        if len(row) < 2:
            continue
        col0 = _clean_text(row[0])
        col1 = _clean_text(row[1])
        if col0 == "כללי" and (
            ("שם" in col1 and "רשות" in col1) or
            ("סמל" in col1 and "רשות" in col1)
        ):
            return True
    return False


# --- פענוח גיליון הפוך (1999, 2002) ---

def _parse_transposed_sheet(all_rows: list[list], year: int) -> pd.DataFrame:
    """
    פענוח גיליון במבנה הפוך:
      - עמודות = רשויות
      - שורות  = מדדים
      - שורות ראשונות = מידע על הרשות (שם, סמל, מחוז, ...)
    """
    if len(all_rows) < 5:
        return pd.DataFrame()

    name_row_idx = symbol_row_idx = None
    for i, row in enumerate(all_rows[:10]):
        if len(row) < 2:
            continue
        label = _clean_text(row[1])
        if name_row_idx is None and "שם" in label and "רשות" in label:
            name_row_idx = i
        if symbol_row_idx is None and "סמל" in label and "רשות" in label:
            symbol_row_idx = i

    if name_row_idx is None or symbol_row_idx is None:
        return pd.DataFrame()

    name_row   = all_rows[name_row_idx]
    symbol_row = all_rows[symbol_row_idx]
    n_cols = max(len(name_row), len(symbol_row))

    col_to_muni: dict[int, dict] = {}
    for col in range(2, n_cols):
        name    = _clean_text(name_row[col]   if col < len(name_row)   else None)
        sym_raw = symbol_row[col] if col < len(symbol_row) else None
        if name and _is_valid_symbol(sym_raw) and not _is_summary_row(name):
            col_to_muni[col] = {
                "name": name,
                "symbol_cbs": _normalize_symbol(sym_raw),
            }

    if not col_to_muni:
        return pd.DataFrame()

    data_start = max(name_row_idx, symbol_row_idx) + 1
    records = []
    current_category = ""

    for row in all_rows[data_start:]:
        if len(row) < 2:
            continue
        cat = _clean_text(row[0])
        if cat:
            current_category = cat
        indicator = _clean_text(row[1])
        if not indicator or len(indicator) < 2:
            continue
        header = f"{current_category} | {indicator}" if current_category else indicator

        for col_idx, muni in col_to_muni.items():
            if col_idx >= len(row):
                continue
            value = _scale_value(header, _clean_value(row[col_idx]))
            if value is not None:
                records.append({
                    "name":          muni["name"],
                    "symbol_cbs":    muni["symbol_cbs"],
                    "column_header": header,
                    "value":         value,
                    "year":          year,
                })

    return pd.DataFrame(records)


# --- פענוח גיליון יחיד ---

def _parse_sheet_rows(all_rows: list[list], year: int) -> pd.DataFrame:
    """מפענח רשימת שורות גולמיות לDataFrame מנורמל."""
    if len(all_rows) < 4:
        return pd.DataFrame()

    header_row_idx = _find_header_row(all_rows)
    headers = _build_headers(all_rows, header_row_idx)
    name_col, sym_col = _find_name_symbol_cols(headers)

    records = []
    for row in all_rows[header_row_idx + 1:]:
        if len(row) <= max(name_col, sym_col):
            continue

        name = _clean_text(row[name_col])
        sym_raw = row[sym_col]

        if not name or _is_summary_row(name):
            continue
        if not _is_valid_symbol(sym_raw):
            continue

        symbol = _normalize_symbol(sym_raw)

        for col_idx, header in enumerate(headers):
            if col_idx in (name_col, sym_col):
                continue
            if not header or col_idx >= len(row):
                continue
            value = _scale_value(header, _clean_value(row[col_idx]))
            if value is not None:
                records.append({
                    "name": name,
                    "symbol_cbs": symbol,
                    "column_header": header,
                    "value": value,
                    "year": year,
                })

    return pd.DataFrame(records)


# --- קריאת קבצים ---

def _read_xls_sheet(file_path: Path, sheet_index: int) -> list[list]:
    wb = xlrd.open_workbook(str(file_path), encoding_override="utf-8")
    if sheet_index >= len(wb.sheets()):
        return []
    ws = wb.sheets()[sheet_index]
    return [[ws.cell(r, c).value for c in range(ws.ncols)] for r in range(ws.nrows)]


def _read_xlsx_sheet(file_path: Path, sheet_name: str) -> list[list]:
    xl = pd.ExcelFile(str(file_path), engine="openpyxl")
    raw = xl.parse(sheet_name, header=None, dtype=str)
    return raw.values.tolist()


# --- גיליונות להתעלם מהם ---

SKIP_SHEETS = {
    "תוכן עניינים", "הערות והסברים", "תיקונים ושינויים",
    "הסברים", "notes", "contents",
    "סיכומים לפי מעמד מוניציפלי",
}


def parse_cbs_file(file_path: Path, year: int) -> dict[str, pd.DataFrame]:
    """מפענח קובץ CBS שלם — מחזיר {sheet_name: DataFrame}.

    כל DataFrame: name, symbol_cbs, column_header, value, year
    """
    ext = file_path.suffix.lower()
    results: dict[str, pd.DataFrame] = {}

    if ext == ".xls":
        try:
            wb = xlrd.open_workbook(str(file_path), encoding_override="utf-8")
        except Exception:
            wb = xlrd.open_workbook(str(file_path), encoding_override="windows-1255")

        for i, sheet_name in enumerate(wb.sheet_names()):
            if any(s in sheet_name for s in SKIP_SHEETS):
                continue
            rows = _read_xls_sheet(file_path, i)
            if _is_transposed(rows):
                df = _parse_transposed_sheet(rows, year)
            else:
                df = _parse_sheet_rows(rows, year)
            if not df.empty:
                results[sheet_name] = df

    elif ext == ".xlsx":
        xl = pd.ExcelFile(str(file_path), engine="openpyxl")
        for sheet_name in xl.sheet_names:
            if any(s in sheet_name for s in SKIP_SHEETS):
                continue
            rows = _read_xlsx_sheet(file_path, sheet_name)
            if _is_transposed(rows):
                df = _parse_transposed_sheet(rows, year)
            else:
                df = _parse_sheet_rows(rows, year)
            if not df.empty:
                results[sheet_name] = df

    return results


def get_municipality_list(file_path: Path) -> list[dict]:
    """חולץ את רשימת הרשויות המלאה מהקובץ."""
    ext = file_path.suffix.lower()

    if ext == ".xls":
        try:
            rows = _read_xls_sheet(file_path, 0)
        except Exception:
            return []
    else:
        xl = pd.ExcelFile(str(file_path), engine="openpyxl")
        # קח את הגיליון הפיזי (לא תוכן עניינים)
        sheet_name = next(
            (s for s in xl.sheet_names if s not in SKIP_SHEETS and "פיזי" in s),
            xl.sheet_names[1] if len(xl.sheet_names) > 1 else xl.sheet_names[0]
        )
        rows = _read_xlsx_sheet(file_path, sheet_name)

    header_row_idx = _find_header_row(rows)
    headers = _build_headers(rows, header_row_idx)
    name_col, sym_col = _find_name_symbol_cols(headers)

    def find_col(keywords: list[str]) -> int:
        for kw in keywords:
            for i, h in enumerate(headers):
                if kw in h:
                    return i
        return -1

    col_district = find_col(["מחוז"])
    col_type = find_col(["מעמד מוניציפלי", "מעמד"])
    col_cluster = find_col(["אשכול"])

    type_map = {
        "עירייה": "עיר", "מועצה מקומית": "מועצה מקומית",
        "מועצה אזורית": "מועצה אזורית",
    }

    municipalities = []
    for row in rows[header_row_idx + 1:]:
        if len(row) <= max(name_col, sym_col):
            continue
        name = _clean_text(row[name_col])
        if not name or _is_summary_row(name):
            continue
        sym_raw = row[sym_col]
        if not _is_valid_symbol(sym_raw):
            continue

        symbol = _normalize_symbol(sym_raw)
        district_raw = _clean_text(row[col_district]) if col_district >= 0 and col_district < len(row) else ""
        district = district_raw.lstrip("ה")
        muni_type_raw = _clean_text(row[col_type]) if col_type >= 0 and col_type < len(row) else ""
        muni_type = type_map.get(muni_type_raw, muni_type_raw)

        cluster = None
        if col_cluster >= 0 and col_cluster < len(row):
            cluster_raw = row[col_cluster]
            if cluster_raw and str(cluster_raw) not in ("nan", "-", ""):
                try:
                    cluster = int(float(str(cluster_raw)))
                except (ValueError, TypeError):
                    pass

        municipalities.append({
            "name": name, "symbol_cbs": symbol,
            "district": district, "municipality_type": muni_type,
            "socioeconomic_cluster": cluster, "name_aliases": [],
        })

    return municipalities
