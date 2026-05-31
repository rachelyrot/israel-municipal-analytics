"""מעדכן את indicators_seed.json עם variants חדשים ומדדים חדשים."""
import json, sys
from pathlib import Path

SEED = Path(__file__).parent.parent / "data" / "seed" / "indicators_seed.json"

with open(SEED, encoding="utf-8") as f:
    indicators = json.load(f)

# ── variants נוספים לאינדיקטורים קיימים ───────────────────────────────────
EXTRA_VARIANTS = {
    "WAGE_AVG": [
        'שכר ורווחה | שכר ממוצע לחודש של שכירים (ש"ח)',
        "שכר ורווחה | שכר ממוצע לחודש של שכירים",
    ],
    "EMP_UNEMP_RATE": [
        'שכר ורווחה | אחוז מקבלי דמי אבטלה מבני 67-20 (שנתי)',
    ],
    "EMP_UNEMP_COUNT": [
        "שכר ורווחה | מקבלי דמי אבטלה \n(ממוצע חודשי)",
        "שכר ורווחה | מקבלי דמי אבטלה (ממוצע חודשי)",
    ],
    "EMP_WELFARE_RECIPIENTS": [
        "שכר ורווחה | מקבלי גמלת הבטחת הכנסה (נפשות, בסוף השנה)",
        "שכר ורווחה | מקבלי גמלת הבטחת הכנסה\n(נפשות, בסוף השנה)",
        "מקבלי הבטחת הכנסה (נפשות)",
    ],
    "WELFARE_ELDERLY": [
        'שכר ורווחה | מקבלי קצבאות זקנה ושאירים סה"כ (סוף שנה)',
        'מקבלי קצבאות זיקנה ושארים - סה"כ',
    ],
    "WELFARE_DISABILITY": [
        "שכר ורווחה | מקבלי גמלאות נכות כללית (סוף שנה)",
        "שכר ורווחה | מקבלי גמלאות נכות כללית\n(סוף שנה)",
        "מקבלי גמלאות נכות כללית",
    ],
    "WELFARE_CHILDREN_FAMILIES": [
        "שכר ורווחה | מספר משפחות של מקבלי קצבאות  בגין ילדים (סוף שנה)",
        "שכר ורווחה | מספר משפחות של מקבלי קצבאות בגין ילדים (סוף שנה)",
    ],
    "WELFARE_CHILDREN_COUNT": [
        "שכר ורווחה | מספר ילדים שבגינם שולמו קצבאות",
        'שכר ורווחה | מספר הילדים הנהנים מקבלת קצבאות בגין ילדים במשפחות עם 2-1 ילדים',
    ],
    "EDU_MATRIC_RATE": [
        "חינוך | אחוז זכאים לתעודת בגרות מבין תלמידי כיתות יב",
        "חינוך | אחוז זכאים לתעודת בגרות מבין תלמידי",
    ],
    "EDU_DROPOUT_RATE": ["חינוך | אחוז תלמידים נושרים"],
    "EDU_TEACHERS": ["חינוך | עובדי הוראה"],
    "EDU_HIGHER_EDUCATION": ["חינוך | תואר אקדמי ראשון"],
    "BUDGET_INCOME_TOTAL": [
        'הכנסות בתקציב הרגיל של הרשויות המקומיות | סה"כ הכנסות בתקציב הרגיל',
    ],
    "BUDGET_INCOME_PC": [
        'הכנסות בתקציב הרגיל של הרשויות המקומיות | הכנסות לנפש בתקציב הרגיל (ש"ח)',
    ],
    "BUDGET_EXPENSE_TOTAL": [
        'הכנסות בתקציב הרגיל של הרשויות המקומיות | סה"כ הוצאות בתקציב הרגיל',
    ],
    "BUDGET_EXPENSE_PC": [
        'הכנסות בתקציב הרגיל של הרשויות המקומיות | הוצאה לנפש בתקציב הרגיל (ש"ח)',
    ],
    "BUDGET_DEFICIT": [
        'הוצאות בתקציב הרגיל של הרשויות המקומיות | עודף/גירעון בתקציב הרגיל השנה',
    ],
    "BUDGET_DEBT": [
        "הוצאות בתקציב הרגיל של הרשויות המקומיות | עומס מלוות לסוף השנה (כולל הפרשי הצמדה)",
    ],
    "ARNONA_INCOME": [
        'הכנסות של הרשות מארנונה (אלפי ש"ח)',
        "הכנסות עצמיות של הרשות מארנונה",
        'הכנסות בתקציב הרגיל של הרשויות המקומיות | הכנסות עצמיות: מארנונה',
    ],
    "ARNONA_RESIDENTIAL_CHARGE": [
        "ארנונה: חיוב בשנת החשבון",
        "ארנונה למגורים - חיוב",
    ],
    "BUILD_STARTS": [
        "בנייה ודיור | התחלת בנייה",
        "בנייה ודיור | התחלות בנייה",
        'התחלת בנייה: מספר דירות',
    ],
    "BUILD_DWELLINGS_TOTAL": [
        "מספר דירות למגורים",
        'מספר דירות למגורים לפי חיובי ארנונה (מאי 2000)',
    ],
    "TRANSPORT_VEHICLES": [
        'כלי רכב מנועיים - סה"כ',
        'מכוניות פרטיות - סה"כ',
    ],
    "INFRA_WATER_TOTAL": [
        'מים | סה"כ צריכת מים (אלפי מ"ק)',
        'מים | סה"כ צריכת מים\n(אלפי מ"ק)',
    ],
    "INFRA_WATER_PC": ['מים | צריכת מים ביתית (מ"ק לנפש)'],
    "INFRA_WATER_LOSS": ['מים | אחוז פחת המים מסך כל תקבולי המים'],
    "SOCIAL_LIFE_SATISFACTION": ["רווחה סובייקטיבית | מרוצים מהחיים"],
    "SOCIAL_NEIGHBORHOOD_SATISFACTION": ["רווחה סובייקטיבית | מרוצים מאזור המגורים"],
    "SOCIAL_HOUSING_SATISFACTION": ["רווחה סובייקטיבית | מרוצים מהדירה"],
    "SOCIAL_TRUST_GOVT": ["רווחה סובייקטיבית | נותנים אמון בממשלה"],
    "SOCIAL_TRUST_PEOPLE": ["רווחה סובייקטיבית | חושבים שניתן לבטוח במרבית האנשים"],
    "SOCIAL_LONELINESS": ["רווחה סובייקטיבית | חשים בדידות"],
    "SOCIAL_VOLUNTEERING": ["רווחה סובייקטיבית | עסקו בפעילות התנדבותית"],
    "SOCIAL_DISCRIMINATION": ["רווחה סובייקטיבית | חשו אפליה כלשהי בשנה האחרונה"],
    "SOCIAL_INTERNET": ["רווחה סובייקטיבית | משתמשים באינטרנט"],
    "SOCIAL_COMMUTE_TIME": ["רווחה סובייקטיבית | משך ההגעה לעבודה"],
    "HEALTH_LIFE_EXPECTANCY": [
        "בריאות | תוחלת חיים בלידה סך הכל",
        "בריאות | תוחלת חיים\nבלידה סך הכל",
    ],
    "HEALTH_DIABETES": ["בריאות | שיעור מקרי סוכרת מתוקנן ל-1,000 תושבים"],
    "HEALTH_GOOD_STATUS_PCT": ["בריאות | מעריכים שמצב בריאותם טוב"],
    "LAND_TOTAL_AREA": ['שימושי קרקע | סך כל שטח השיפוט', 'שימושי קרקע | שטח (קמ"ר)'],
    "POP_TOTAL": [
        'סה"כ  אוכלוסייה בסוף השנה',
        'דמוגרפיה | סה"כ  אוכלוסייה בסוף השנה',
        "דמוגרפיה | סה\"כ אוכלוסייה",
    ],
    "POP_BIRTHS": ["דמוגרפיה | לידות חי", "גידול טבעי ועלייה | לידות חי"],
    "POP_DEATHS": ["דמוגרפיה | פטירות", "גידול טבעי ועלייה | פטירות"],
    "POP_MIGRATION_BALANCE": [
        'דמוגרפיה | מאזן הגירה ביישוב סה"כ',
        'דמוגרפיה | מאזן הגירה - סה"כ',
        "גידול טבעי ועלייה | מאזן הגירה - סה\"כ",
    ],
    "POP_NATURAL_INCREASE": [
        "דמוגרפיה | ריבוי טבעי ל-1,000 תושבים",
        "דמוגרפיה | ריבוי טבעי  ל-1,000 תושבים",
        "גידול טבעי ועלייה | ריבוי טבעי ל-1,000 תושבים",
    ],
    "POP_AGE_65_PLUS": [
        "דמוגרפיה | בני 65 ומעלה",
        "דמוגרפיה | 65+",
    ],
    "POP_GROWTH_RATE": [
        "דמוגרפיה | אחוז גידול האוכלוסייה לעומת השנה הקודמת",
    ],
    "TRANSPORT_ACCIDENTS_RATE": [
        "תחבורה | תאונות דרכים עם נפגעים שיעור ל-1,000 תושבים",
    ],
    "TRANSPORT_FATALITIES": ["תחבורה | הרוגים"],
}

updated_count = 0
for ind in indicators:
    if ind["code"] in EXTRA_VARIANTS:
        existing = set(ind["cbs_column_variants"])
        for v in EXTRA_VARIANTS[ind["code"]]:
            if v not in existing:
                ind["cbs_column_variants"].append(v)
                updated_count += 1

# ── מדדים חדשים ────────────────────────────────────────────────────────────
NEW_INDICATORS = [
    {"code": "EMP_UNEMP_AVG_AGE", "name_he": "גיל ממוצע מקבלי דמי אבטלה", "domain": "employment", "unit": "שנים", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['גיל ממוצע של מקבלי דמי אבטלה (לא כולל חיילים)', 'שכר ורווחה | גיל ממוצע של מקבלי דמי אבטלה (לא כולל חיילים)', 'גיל ממוצע של מקבלי דמי אבטלה']},
    {"code": "EMP_UNEMP_DAILY_BENEFIT", "name_he": "דמי אבטלה ממוצעים ליום", "domain": "employment", "unit": "₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['דמי אבטלה ממוצעים ליום (ש"ח)', 'שכר ורווחה | דמי אבטלה ממוצעים ליום (ש"ח)']},
    {"code": "EMP_VOCATIONAL_TRAINING", "name_he": "מקבלי הכשרה מקצועית", "domain": "employment", "unit": "נפש", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['מקבלי הכשרה מקצועית - סה"כ', 'שכר ורווחה | מקבלי הכשרה מקצועית - סה"כ']},
    {"code": "HEALTH_HMO_CLALIT_PCT", "name_he": 'מבוטחי קופ"ח כללית', "domain": "health", "unit": "%", "is_percentage": True, "higher_is_better": None,
     "cbs_column_variants": ['אחוז המבוטחים בקופ"ח כללית מתוך סך כל המבוטחים', 'שכר ורווחה | אחוז המבוטחים בקופ"ח כללית מתוך סך כל המבוטחים']},
    {"code": "HEALTH_HMO_MACCABI_PCT", "name_he": 'מבוטחי קופ"ח מכבי', "domain": "health", "unit": "%", "is_percentage": True, "higher_is_better": None,
     "cbs_column_variants": ['אחוז המבוטחים בקופ"ח מכבי מתוך סך כל המבוטחים', 'שכר ורווחה | אחוז המבוטחים בקופ"ח מכבי מתוך סך כל המבוטחים']},
    {"code": "HEALTH_HMO_MEUHEDET_PCT", "name_he": 'מבוטחי קופ"ח מאוחדת', "domain": "health", "unit": "%", "is_percentage": True, "higher_is_better": None,
     "cbs_column_variants": ['אחוז המבוטחים בקופ"ח מאוחדת מתוך סך כל המבוטחים', 'שכר ורווחה | אחוז המבוטחים בקופ"ח מאוחדת מתוך סך כל המבוטחים']},
    {"code": "HEALTH_HMO_LEUMIT_PCT", "name_he": 'מבוטחי קופ"ח לאומית', "domain": "health", "unit": "%", "is_percentage": True, "higher_is_better": None,
     "cbs_column_variants": ['אחוז המבוטחים בקופ"ח לאומית מתוך סך כל המבוטחים', 'שכר ורווחה | אחוז המבוטחים בקופ"ח לאומית מתוך סך כל המבוטחים']},
    {"code": "BUDGET_INCOME_EDU", "name_he": "הכנסות מחינוך", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['הכנסות של הרשות מחינוך (אלפי ש"ח)', 'הכנסות בתקציב הרגיל של הרשויות המקומיות | הכנסות של הרשות מחינוך (אלפי ש"ח)']},
    {"code": "BUDGET_INCOME_WELFARE", "name_he": "הכנסות מרווחה", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['הכנסות של הרשות מרווחה (אלפי ש"ח)', 'הכנסות בתקציב הרגיל של הרשויות המקומיות | הכנסות של הרשות מרווחה (אלפי ש"ח)']},
    {"code": "BUDGET_INCOME_WATER_UTIL", "name_he": "הכנסות ממפעל המים", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['הכנסות של הרשות ממפעל המים (אלפי ש"ח)', 'הכנסות בתקציב הרגיל של הרשויות המקומיות | הכנסות של הרשות ממפעל המים (אלפי ש"ח)']},
    {"code": "BUDGET_EXPENSE_OPS", "name_he": "הוצאות לפעולות", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['הוצאות של הרשות לפעולות (אלפי ש"ח)', 'הוצאות בתקציב הרגיל של הרשויות המקומיות | הוצאות של הרשות לפעולות (אלפי ש"ח)']},
    {"code": "BUDGET_EXPENSE_FINANCE", "name_he": "הוצאות מימון", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['הוצאות מימון של הרשות (אלפי ש"ח)', 'הוצאות בתקציב הרגיל של הרשויות המקומיות | הוצאות מימון של הרשות (אלפי ש"ח)']},
    {"code": "BUDGET_CAPITAL_EXPENSE", "name_he": "הוצאות תקציב בלתי רגיל", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['סה"כ הוצאות של הרשות בתקציב בלתי רגיל (אלפי ש"ח)']},
    {"code": "BUDGET_CAPITAL_INCOME", "name_he": "הכנסות תקציב בלתי רגיל", "domain": "budget", "unit": "אלפי ₪", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['סה"כ הכנסות של הרשות מתקציב בלתי רגיל (אלפי ש"ח)']},
    {"code": "SOCIAL_ECONOMIC_SATISFACTION", "name_he": "שביעות רצון מהמצב הכלכלי", "domain": "social", "unit": "%", "is_percentage": True, "higher_is_better": True,
     "cbs_column_variants": ['שביעות רצון מהמצב הכלכלי', 'רווחה סובייקטיבית | שביעות רצון מהמצב הכלכלי']},
    {"code": "SOCIAL_FUTURE_OPTIMISM", "name_he": "הערכת החיים בעתיד", "domain": "social", "unit": "%", "is_percentage": True, "higher_is_better": True,
     "cbs_column_variants": ['הערכת החיים בעתיד', 'הערכת המצב הכלכלי בעתיד', 'רווחה סובייקטיבית | הערכת החיים בעתיד']},
    {"code": "EDU_HIGHSCHOOLS", "name_he": "בתי ספר על יסודיים", "domain": "education", "unit": "בתי ספר", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['חינוך | בתי ספר על יסודיים - סה"כ', 'בתי ספר על יסודיים - סה"כ']},
    {"code": "EDU_MIDDLE_SCHOOLS", "name_he": "בתי ספר חטיבות ביניים", "domain": "education", "unit": "בתי ספר", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['חינוך | בתי ספר בחטיבות ביניים', 'בתי ספר בחטיבות ביניים']},
    {"code": "EDU_HIGH_SCHOOLS", "name_he": "בתי ספר תיכוניים", "domain": "education", "unit": "בתי ספר", "is_percentage": False, "higher_is_better": None,
     "cbs_column_variants": ['חינוך | בתי ספר תיכוניים', 'בתי ספר תיכוניים']},
]

existing_codes = {i["code"] for i in indicators}
added_new = 0
for ni in NEW_INDICATORS:
    if ni["code"] not in existing_codes:
        indicators.append(ni)
        added_new += 1

with open(SEED, "w", encoding="utf-8") as f:
    json.dump(indicators, f, ensure_ascii=False, indent=2)

print(f"Variants added to existing indicators: {updated_count}")
print(f"New indicators added: {added_new}")
print(f"Total indicators: {len(indicators)}")
print("Saved OK")

# ── סנכרון ל-DB ────────────────────────────────────────────────────────────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models.indicator import Indicator as IndicatorModel

db = SessionLocal()
db_updated = 0
db_added = 0
try:
    for item in indicators:
        row = db.query(IndicatorModel).filter_by(code=item["code"]).first()
        if row:
            row.cbs_column_variants = item.get("cbs_column_variants", [])
            db_updated += 1
        else:
            db.add(IndicatorModel(**item))
            db_added += 1
    db.commit()
    print(f"DB synced: {db_updated} updated, {db_added} added")
finally:
    db.close()
