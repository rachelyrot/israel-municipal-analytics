"""Analyze unmapped columns - identify which clearly map to existing indicators."""
import json, os, sys
from pathlib import Path

os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:1234@localhost:5432/israel_municipal'
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services.ingestion.pipeline import _build_indicator_map, _find_indicator_id

db = SessionLocal()
ind_map = _build_indicator_map(db)
db.close()

# Load unmapped
with open('data/uploads/unmapped_columns.json', encoding='utf-8') as f:
    unmapped = json.load(f)

print("=== VARIANT PATTERNS TO ADD ===")
print("These unmapped headers appear to map to existing indicators via substring matching")
print("or are alternative phrasing:\n")

# Group patterns by likely indicator
groups = {
    "POP_TOTAL": ["סה\"כ  אוכלוסייה", "סה\"כ אוכלוסייה", "אוכלוסייה בסוף שנה", "דמוגרפיה | אוכלוסייה סה\"כ"],
    "POP_NATURAL_INCREASE": ["ריבוי טבעי סה\"כ", "ריבוי טבעי - סה\"כ", "דמוגרפיה | ריבוי טבעי - סה\"כ", "דמוגרפיה | ריבוי טבעי סה\"כ"],
    "EMP_UNEMP_COUNT": ["מקבלי דמי אבטלה - גברים", "שכר ורווחה | מקבלי דמי אבטלה - גברים"],
    "WELFARE_DISABILITY": ["שכר ורווחה | מקבלי גמלאות נכות כללית", "מקבלי גמלאות נכות כללית"],
    "BUDGET_INCOME_TOTAL": [
        "סה\"כ הכנסות של הרשות מן התקציב הרגיל (אלפי ש\"ח)",
        "הכנסות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הכנסות של הרשות (אלפי ש\"ח)",
        "הכנסות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הכנסות של הרשות מן התקציב הרגיל (אלפי ש\"ח)",
        "סה\"כ הכנסות בתקציב הרגיל",
    ],
    "BUDGET_INCOME_PC": [
        "הכנסות של הרשות (ש\"ח לנפש)",
        "הכנסות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הכנסות של הרשות (ש\"ח לנפש)",
        "הכנסות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הכנסות של הרשות מן התקציב הרגיל (ש\"ח לנפש)",
    ],
    "BUDGET_EXPENSE_TOTAL": [
        "סה\"כ הוצאות של הרשות בתקציב רגיל (אלפי ש\"ח)",
        "הוצאות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הוצאות של הרשות (אלפי ש\"ח)",
        "הוצאות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הוצאות של הרשות בתקציב רגיל (אלפי ש\"ח)",
        "סה\"כ הוצאות של הרשות (אלפי ש\"ח)",
    ],
    "BUDGET_EXPENSE_PC": [
        "הוצאות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הוצאות של הרשות (ש\"ח לנפש)",
        "הוצאות בתקציב הרגיל של הרשויות המקומיות | סה\"כ הוצאות של הרשות בתקציב רגיל (ש\"ח לנפש)",
    ],
    "EDU_STUDENTS_TOTAL": [
        "תלמידים - סה\"כ",
        "חינוך | כיתות - סה\"כ",
    ],
    "BUILD_STARTS": [
        "בנייה ודיור | התחלת בנייה",
        "בנייה | התחלת בנייה",
    ],
    "INFRA_WATER_TOTAL": [
        "מים | תקבולי מים (אלפי מ\"ק)",
    ],
    "TRANSPORT_VEHICLES": [
        "כלי רכב פרטיים סה\"כ",
        "מכוניות פרטיות - סה\"כ",
    ],
}

for code, variants in groups.items():
    matched = [v for v, c in unmapped if v in variants]
    if matched:
        print(f"  {code}: {matched}")

print("\n=== ALL UNMAPPED (count >= 6) that need review ===")
for h, c in unmapped:
    if c >= 6:
        # Check it's really unmapped
        if not _find_indicator_id(h, ind_map):
            print(f"  {c}x  {h[:80]}")
