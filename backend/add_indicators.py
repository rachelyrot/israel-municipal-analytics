# -*- coding: utf-8 -*-
"""Append new indicator definitions to indicators_seed.json."""
import json
from pathlib import Path

SEED_PATH = Path("data/seed/indicators_seed.json")

NEW_INDICATORS = [
    # ── HEALTH ──────────────────────────────────────────────────────────────
    {
        "code": "HEALTH_CANCER_MEN",
        "name_he": "מקרי סרטן – גברים",
        "domain": "health",
        "unit": "מקרים בשנה",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2018-2014 | מספר מקרי סרטן ממוצע לשנה, גברים",
            "מספר מקרי סרטן ממוצע לשנה, גברים",
        ],
    },
    {
        "code": "HEALTH_CANCER_WOMEN",
        "name_he": "מקרי סרטן – נשים",
        "domain": "health",
        "unit": "מקרים בשנה",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2018-2014 | מספר מקרי סרטן ממוצע לשנה, נשים",
            "מספר מקרי סרטן ממוצע לשנה, נשים",
        ],
    },
    {
        "code": "HEALTH_CANCER_RATE_MEN",
        "name_he": "שיעור סרטן (מתוקנן) – גברים",
        "domain": "health",
        "unit": "ל-100,000 תושבים",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2018-2014 | שיעור סרטן מכל הסוגים מתוקנן ל-100,000 תושבים, גברים",
            "שיעור סרטן מכל הסוגים מתוקנן ל-100,000 תושבים, גברים",
        ],
    },
    {
        "code": "HEALTH_CANCER_RATE_WOMEN",
        "name_he": "שיעור סרטן (מתוקנן) – נשים",
        "domain": "health",
        "unit": "ל-100,000 תושבים",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2018-2014 | שיעור סרטן מכל הסוגים מתוקנן ל-100,000 תושבים, נשים",
            "שיעור סרטן מכל הסוגים מתוקנן ל-100,000 תושבים, נשים",
        ],
    },
    {
        "code": "HEALTH_DIABETES",
        "name_he": "מקרי סוכרת",
        "domain": "health",
        "unit": "מקרים בשנה",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2022-2020 | מספר מקרי סוכרת ממוצע לשנה",
            "מספר מקרי סוכרת ממוצע לשנה",
        ],
    },
    {
        "code": "HEALTH_CHRONIC_PROBLEM",
        "name_he": "בעיה בריאותית מתמשכת",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "יש בעיה בריאותית מתמשכת המפריעה בתפקוד",
        ],
    },
    {
        "code": "HEALTH_SEVERE_DISABILITY",
        "name_he": "מוגבלות תפקודית חמורה",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "יש מוגבלות תפקודית חמורה",
        ],
    },
    {
        "code": "HEALTH_MENTAL_DISABILITY",
        "name_he": "מוגבלות נפשית",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "מוגבלות נפשית",
        ],
    },
    {
        "code": "HEALTH_PHYSICAL_DISABILITY",
        "name_he": "מוגבלות פיזית",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "מוגבלות פיזית",
        ],
    },
    {
        "code": "HEALTH_INTELLECTUAL_DISABILITY",
        "name_he": "מוגבלות שכלית-התפתחותית",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "מוגבלות שכלית התפתחותית",
        ],
    },
    {
        "code": "HEALTH_VISUAL_IMPAIRMENT",
        "name_he": "לקויות ראייה",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "לקויות ראייה",
        ],
    },
    {
        "code": "HEALTH_HEARING_IMPAIRMENT",
        "name_he": "לקויות שמיעה",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "לקויות שמיעה",
        ],
    },
    {
        "code": "HEALTH_AUTISM",
        "name_he": "רצף אוטיסטי",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "רצף אוטיסטי",
        ],
    },
    {
        "code": "HEALTH_CHRONIC_DISEASES",
        "name_he": "מחלות כרוניות",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "מחלות כרוניות",
        ],
    },
    {
        "code": "HEALTH_INSURED_PCT",
        "name_he": "מבוטחים בקופת חולים",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            'אחוז המבוטחים בקופ"ח מתוך סך כל המבוטחים',
        ],
    },
    {
        "code": "HEALTH_DEPRESSION",
        "name_he": "חשים דיכאון",
        "domain": "health",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "חשים דיכאון",
        ],
    },
    # ── WELFARE ─────────────────────────────────────────────────────────────
    {
        "code": "WELFARE_NURSING_HOME_PCT",
        "name_he": "דיירים בבתי אבות ודיור מוגן",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "אחוז דיירים בבתי אבות ובדיור מוגן",
        ],
    },
    {
        "code": "WELFARE_NURSING_ALLOWANCE",
        "name_he": "מקבלי גמלת סיעוד",
        "domain": "welfare",
        "unit": "נפשות",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "גמלת סיעוד מהמוסד לביטוח לאומי",
        ],
    },
    # ── WELLBEING ────────────────────────────────────────────────────────────
    {
        "code": "WELLBEING_NEIGHBORHOOD_COOP",
        "name_he": "שיתוף פעולה שכונתי",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "אנשים בשכונה משתפים פעולה כדי לשפר את השכונה",
        ],
    },
    {
        "code": "WELLBEING_CIVIC_ENGAGEMENT",
        "name_he": "מעורבות בחיים הציבוריים",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "היו מעורבים בחיים הציבוריים",
        ],
    },
    {
        "code": "WELLBEING_DISTRUST",
        "name_he": "חוסר אמון בין-אישי",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "חושבים שבאופן כללי יש להיזהר מאנשים",
        ],
    },
    {
        "code": "WELLBEING_POLITICAL_EFFICACY",
        "name_he": "תחושת השפעה על מדיניות",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "חושבים שיכולים להשפיע על מדיניות הממשלה",
        ],
    },
    {
        "code": "WELLBEING_HEALTH_SYSTEM",
        "name_he": "שביעות רצון ממערכת הבריאות",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "חושבים שתפקוד מערכת הבריאות טוב",
        ],
    },
    {
        "code": "WELLBEING_EDU_SYSTEM",
        "name_he": "שביעות רצון ממערכת החינוך",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "חושבים שתפקוד מערכת החינוך טוב",
        ],
    },
    {
        "code": "WELLBEING_SOCIAL_SUPPORT",
        "name_he": "תמיכה חברתית בעת משבר",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "חשים שיש על מי לסמוך בעת משבר",
        ],
    },
    {
        "code": "WELLBEING_COPING",
        "name_he": "מתמודדים עם בעיותיהם",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מצליחים להתמודד עם בעיותיהם תמיד או לעיתים קרובות",
        ],
    },
    {
        "code": "WELLBEING_WORK_LIFE_BALANCE",
        "name_he": "איזון עבודה-חיים",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מרוצים מהאיזון בין העבודה לתחומי חיים אחרים",
        ],
    },
    {
        "code": "WELLBEING_JOB_SATISFACTION",
        "name_he": "שביעות רצון מהעבודה",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מרוצים מהעבודה",
        ],
    },
    {
        "code": "WELLBEING_INCOME_SATISFACTION",
        "name_he": "שביעות רצון מהשכר",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מרוצים מההכנסה מהעבודה",
        ],
    },
    {
        "code": "WELLBEING_NEIGHBOR_SATISFACTION",
        "name_he": "שביעות רצון מהשכנים",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מרוצים מהקשר עם השכנים",
        ],
    },
    {
        "code": "WELLBEING_HEALTH_TRUST",
        "name_he": "אמון במערכת הבריאות",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "נותנים אמון במערכת הבריאות",
        ],
    },
    {
        "code": "WELLBEING_JUSTICE_TRUST",
        "name_he": "אמון במערכת המשפט",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "נותנים אמון במערכת המשפט",
        ],
    },
    {
        "code": "WELLBEING_NOISE",
        "name_he": "הפרעת רעש מחוץ לדירה",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "רעש מחוץ לדירה מפריע או מפריע מאוד",
        ],
    },
    # ── POPULATION ──────────────────────────────────────────────────────────
    {
        "code": "POP_MALE_TOTAL",
        "name_he": "גברים סוף שנה",
        "domain": "population",
        "unit": "נפשות",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ גברים בסוף השנה",
            "גברים | סך הכל",
        ],
    },
    {
        "code": "POP_FEMALE_TOTAL",
        "name_he": "נשים סוף שנה",
        "domain": "population",
        "unit": "נפשות",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ נשים בסוף השנה",
            "נשים | סך הכל",
        ],
    },
    {
        "code": "POP_JEWISH_PCT",
        "name_he": "יהודים (מתוך יהודים ואחרים)",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "יהודים (אחוזים מתוך יהודים ואחרים)",
        ],
    },
    {
        "code": "POP_ARAB_PCT",
        "name_he": "ערבים (מתוך כלל הישראלים)",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "ערבים (אחוזים מתוך כלל אוכלוסיית הישראלים)",
        ],
    },
    {
        "code": "POP_MUSLIM_PCT",
        "name_he": "מוסלמים (מתוך האוכלוסייה הערבית)",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "מוסלמים (אחוזים מתוך האוכלוסייה הערבית)",
        ],
    },
    {
        "code": "POP_CHRISTIAN_PCT",
        "name_he": "נוצרים (מתוך האוכלוסייה הערבית)",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "נוצרים (אחוזים מתוך האוכלוסייה הערבית)",
        ],
    },
    {
        "code": "POP_DRUZE_PCT",
        "name_he": "דרוזים (מתוך האוכלוסייה הערבית)",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "דרוזים (אחוזים מתוך האוכלוסייה הערבית)",
        ],
    },
    # ── MARITAL STATUS ───────────────────────────────────────────────────────
    {
        "code": "MARITAL_SINGLE",
        "name_he": "רווקים",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "מצב משפחתי מתוך בני 18 ומעלה | 2023 | רווקים",
            "רווקים | סך הכל",
            "רווקים",
        ],
    },
    {
        "code": "MARITAL_MARRIED",
        "name_he": "נשואים",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "נשואים",
            "נשואים | סך הכל",
        ],
    },
    {
        "code": "MARITAL_DIVORCED",
        "name_he": "גרושים",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "גרושים",
            "גרושים | סך הכל",
        ],
    },
    {
        "code": "MARITAL_WIDOWED",
        "name_he": "אלמנים",
        "domain": "population",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "אלמנים",
            "אלמנים | סך הכל",
        ],
    },
    # ── EDUCATION ────────────────────────────────────────────────────────────
    {
        "code": "EDU_LEVEL_PRIMARY_MINUS",
        "name_he": "השכלה נמוכה מיסודי",
        "domain": "education",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2023 | השכלה נמוכה מסיום בית ספר יסודי (8 שנתי)",
            "השכלה נמוכה מסיום בית ספר יסודי (8 שנתי)",
        ],
    },
    {
        "code": "EDU_LEVEL_NO_BAGRUT",
        "name_he": "תיכון ללא בגרות",
        "domain": "education",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2023 | סיום בית ספר תיכון ללא תעודת בגרות",
            "סיום בית ספר תיכון ללא תעודת בגרות",
        ],
    },
    {
        "code": "EDU_LEVEL_POST_HIGH",
        "name_he": "תעודה על-תיכונית לא-אקדמית",
        "domain": "education",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2023 | תעודה על-תיכונית לא-אקדמית",
            "תעודה על-תיכונית לא-אקדמית",
        ],
    },
    {
        "code": "EDU_LEVEL_MA",
        "name_he": "תואר שני",
        "domain": "education",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2023 | תואר אקדמי שני",
            "תואר אקדמי שני",
        ],
    },
    {
        "code": "EDU_LEVEL_PHD",
        "name_he": "תואר שלישי",
        "domain": "education",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2023 | תואר אקדמי שלישי",
            "תואר אקדמי שלישי",
        ],
    },
    {
        "code": "EDU_KINDERGARTEN",
        "name_he": "ילדים בגנים (משרד החינוך)",
        "domain": "education",
        "unit": "ילדים",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "חינוך והשכלה | תשפ\"ד 2023/24 | ילדים בגנים של משרד החינוך",
            "ילדים בגנים של משרד החינוך",
        ],
    },
    {
        "code": "EDU_SCHOOLS_CURRENT",
        "name_he": "בתי ספר (עדכני)",
        "domain": "education",
        "unit": "בתי ספר",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תשפ\"ד 2023/24 | בתי ספר",
            "תשפ\"ה 2024/25 | בתי ספר",
        ],
    },
    {
        "code": "EDU_STUDENTS_CURRENT",
        "name_he": "תלמידים (עדכני)",
        "domain": "education",
        "unit": "תלמידים",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תשפ\"ד 2023/24 | תלמידים",
            "תשפ\"ה 2024/25 | תלמידים",
        ],
    },
    {
        "code": "EDU_CLASSES_CURRENT",
        "name_he": "כיתות (עדכני)",
        "domain": "education",
        "unit": "כיתות",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תשפ\"ד 2023/24 | כיתות",
        ],
    },
    # ── EMPLOYMENT ───────────────────────────────────────────────────────────
    {
        "code": "EMP_UNEMPLOYMENT_RATE",
        "name_he": "שיעור מקבלי דמי אבטלה",
        "domain": "employment",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "אחוז מקבלי דמי אבטלה מבני 67-20 (ממוצע חודשי)",
        ],
    },
    {
        "code": "EMP_UNEMPLOYMENT_COUNT",
        "name_he": "מקבלי דמי אבטלה (סה\"כ שנתי)",
        "domain": "employment",
        "unit": "נפשות",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "מספר מקבלי דמי אבטלה (סה\"כ שנתי)",
        ],
    },
    {
        "code": "EMP_UNEMPLOYMENT_DAYS",
        "name_he": "ימי זכאות לדמי אבטלה (ממוצע)",
        "domain": "employment",
        "unit": "ימים",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "ימי זכאות לדמי אבטלה (ממוצע שנתי)",
        ],
    },
    {
        "code": "EMP_BELOW_MEDIAN_WAGE",
        "name_he": "שכירים מתחת לשכר החציוני",
        "domain": "employment",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2023 | שכירים המשתכרים מתחת לשכר החציוני",
            "שכירים המשתכרים מתחת לשכר החציוני",
        ],
    },
    {
        "code": "EMP_BELOW_MIN_WAGE",
        "name_he": "שכירים מתחת לשכר מינימום",
        "domain": "employment",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2023 | שכירים המשתכרים מתחת לשכר המינימום",
            "שכירים המשתכרים מתחת לשכר המינימום",
        ],
    },
    {
        "code": "INC_NET_PER_CAPITA",
        "name_he": "הכנסה נטו לנפש",
        "domain": "employment",
        "unit": "ש\"ח",
        "is_percentage": False,
        "higher_is_better": True,
        "cbs_column_variants": [
            "מתוך סקר הוצאות משק בית | 2023 | הכנסה כספית נטו לנפש",
            "הכנסה כספית נטו לנפש",
        ],
    },
    {
        "code": "EXP_PER_CAPITA",
        "name_he": "הוצאה כספית לנפש",
        "domain": "employment",
        "unit": "ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2023 | הוצאה כספית לנפש",
            "הוצאה כספית לנפש",
        ],
    },
    # ── PERIPHERY INDEX ──────────────────────────────────────────────────────
    {
        "code": "PERIPHERY_INDEX",
        "name_he": "מדד פריפריאליות",
        "domain": "population",
        "unit": "ערך מדד",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2020 | ערך מדד",
        ],
    },
    {
        "code": "PERIPHERY_RANK",
        "name_he": "דירוג פריפריאליות",
        "domain": "population",
        "unit": "דירוג",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2020 | דירוג (מ-1 עד 255, 1 הפריפריאלי ביותר)",
        ],
    },
    {
        "code": "PERIPHERY_DISTANCE_TA",
        "name_he": "מרחק ממחוז תל אביב (ק\"מ)",
        "domain": "population",
        "unit": "ק\"מ",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2020 | מרחק מגבול מחוז תל אביב (ק\"מ)",
            "מרחק מגבול מחוז תל אביב (ק\"מ)",
        ],
    },
    # ── SOCIOECONOMIC INDEX 2021 ─────────────────────────────────────────────
    {
        "code": "SOCIOECO_RANK_2021",
        "name_he": "דירוג חברתי-כלכלי 2021",
        "domain": "population",
        "unit": "דירוג",
        "is_percentage": False,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2021 | דירוג (מ-1 עד 255, 1 הנמוך ביותר)",
        ],
    },
    {
        "code": "SOCIOECO_INDEX_2021",
        "name_he": "ערך מדד חברתי-כלכלי 2021",
        "domain": "population",
        "unit": "ערך מדד",
        "is_percentage": False,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2021 | ערך מדד",
        ],
    },
    {
        "code": "SOCIOECO_HEALTH_WELFARE_2021",
        "name_he": "מרכיב בריאות ורווחה (מדד ח\"כ 2021)",
        "domain": "welfare",
        "unit": "ערך מדד",
        "is_percentage": False,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2021 | בריאות ורווחה",
        ],
    },
    {
        "code": "SOCIOECO_EDUCATION_2021",
        "name_he": "מרכיב חינוך (מדד ח\"כ 2021)",
        "domain": "education",
        "unit": "ערך מדד",
        "is_percentage": False,
        "higher_is_better": True,
        "cbs_column_variants": [
            "2021 | חינוך והשכלה",
        ],
    },
    # ── LAND USE 2021 ────────────────────────────────────────────────────────
    {
        "code": "LAND_BUILT_2021",
        "name_he": "שטח בנוי 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | שטח בנוי",
        ],
    },
    {
        "code": "LAND_AGRI_2021",
        "name_he": "שטח חקלאי 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | שטח חקלאי",
        ],
    },
    {
        "code": "LAND_FOREST_2021",
        "name_he": "יער וחורש 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | יער וחורש",
            "2021 | יער, חורש ופארקים",
        ],
    },
    {
        "code": "LAND_CROPS_2021",
        "name_he": "גידולי שדה 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | גידולי שדה",
        ],
    },
    {
        "code": "LAND_ORCHARDS_2021",
        "name_he": "מטעים 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | מטעים",
        ],
    },
    {
        "code": "LAND_COMMERCE_2021",
        "name_he": "מסחר ומשרדים 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | מסחר ומשרדים",
        ],
    },
    {
        "code": "LAND_PUBLIC_SERVICES_2021",
        "name_he": "שירותים ציבוריים 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | שירותים ציבוריים",
        ],
    },
    {
        "code": "LAND_INFRA_2021",
        "name_he": "תשתית ותחבורה 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | תשתית ותחבורה",
        ],
    },
    {
        "code": "LAND_NATURAL_2021",
        "name_he": "קרקע טבעית ורוקה 2021",
        "domain": "infrastructure",
        "unit": "דונם",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "2021 | קרקע, סלע, שיחים, שטח חפור וגופי מים",
        ],
    },
    # ── WATER / ENVIRONMENT ──────────────────────────────────────────────────
    {
        "code": "WATER_MICRO_VIOLATIONS",
        "name_he": "חריגות מיקרוביאליות במי שתייה",
        "domain": "infrastructure",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "אחוז חריגות בבדיקות מיקרוביאליות במי שתייה",
        ],
    },
    {
        "code": "WATER_SEWAGE_TREATMENT",
        "name_he": "שפכים מטופלים ברמה שניונית+",
        "domain": "infrastructure",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": True,
        "cbs_column_variants": [
            "אחוז השפכים המטופלים ברמה שניונית ומעלה",
        ],
    },
    # ── INFRASTRUCTURE ───────────────────────────────────────────────────────
    {
        "code": "INFRA_CAR_AGE",
        "name_he": "גיל ממוצע של רכב פרטי",
        "domain": "infrastructure",
        "unit": "שנים",
        "is_percentage": False,
        "higher_is_better": False,
        "cbs_column_variants": [
            "גיל ממוצע של רכב פרטי (שנים)",
        ],
    },
    # ── HOUSING ─────────────────────────────────────────────────────────────
    {
        "code": "HOUSING_RENTAL_PCT",
        "name_he": "דירות בשכירות",
        "domain": "infrastructure",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": None,
        "cbs_column_variants": [
            "דירות בשכירות",
        ],
    },
    # ── CRIME ────────────────────────────────────────────────────────────────
    {
        "code": "CRIME_CONVICTED_PCT",
        "name_he": "מורשעים בדין (% מבוגרים)",
        "domain": "welfare",
        "unit": "%",
        "is_percentage": True,
        "higher_is_better": False,
        "cbs_column_variants": [
            "2023 | מבוגרים תושבי ישראל המורשעים בדין לפי קבוצת עבירה באחוזים",
            "פשיעה ומשפט (ברשויות המונות 50,000 תושבים ויותר) | 2023 | מבוגרים תושבי ישראל המורשעים בדין, לפי רשות מקומית שבה גרו",
            "מבוגרים תושבי ישראל המורשעים בדין לפי קבוצת עבירה באחוזים",
        ],
    },
    # ── BUDGET – GOVERNMENT INCOME ──────────────────────────────────────────
    {
        "code": "BUDGET_GOV_TOTAL",
        "name_he": "הכנסות מהממשלה (סה\"כ)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ הכנסות מהממשלה",
            "הכנסות | סה\"כ הכנסות מהממשלה",
        ],
    },
    {
        "code": "BUDGET_GOV_EDU",
        "name_he": "הכנסות ממשרד החינוך",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הכנסות מהממשלה: ממשרד החינוך",
        ],
    },
    {
        "code": "BUDGET_GOV_WELFARE",
        "name_he": "הכנסות ממשרד הרווחה",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הכנסות מהממשלה: ממשרד הרווחה",
        ],
    },
    {
        "code": "BUDGET_GOV_GENERAL_GRANT",
        "name_he": "מענק כללי מהממשלה",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הכנסות מהממשלה: מענק כללי",
        ],
    },
    {
        "code": "BUDGET_GOV_SPECIAL_GRANTS",
        "name_he": "מענקים מיוחדים מהממשלה",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הכנסות מהממשלה: מענקים מיוחדים ומיועדים",
        ],
    },
    # ── BUDGET – LABOR COSTS ─────────────────────────────────────────────────
    {
        "code": "BUDGET_LABOR_TOTAL",
        "name_he": "עלות עבודה (סה\"כ)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ הוצאות לעלות עבודה",
            "הוצאות לעלות עבודה | סה\"כ",
        ],
    },
    {
        "code": "BUDGET_LABOR_EDU",
        "name_he": "עלות עבודה – חינוך",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הוצאות לעלות עבודה: לחינוך",
        ],
    },
    {
        "code": "BUDGET_LABOR_WELFARE",
        "name_he": "עלות עבודה – רווחה",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הוצאות לעלות עבודה: לרווחה",
        ],
    },
    # ── BUDGET – STATE SERVICES ──────────────────────────────────────────────
    {
        "code": "BUDGET_STATE_TOTAL",
        "name_he": "שירותים ממלכתיים (סה\"כ)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ שירותים ממלכתיים",
            "תקבולים בתקציב הרגיל - לפי פרקי תקציב | סה\"כ שירותים ממלכתיים",
        ],
    },
    {
        "code": "BUDGET_STATE_EDU",
        "name_he": "שירותים ממלכתיים – חינוך",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "שירותים ממלכתיים - חינוך",
            "שירותים ממלכתיים: חינוך",
            "תשלומים בתקציב הרגיל - לפי פרקי תקציב | שירותים ממלכתיים: חינוך",
        ],
    },
    {
        "code": "BUDGET_STATE_WELFARE",
        "name_he": "שירותים ממלכתיים – רווחה",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "שירותים ממלכתיים - רווחה",
            "שירותים ממלכתיים: רווחה",
        ],
    },
    {
        "code": "BUDGET_STATE_CULTURE",
        "name_he": "שירותים ממלכתיים – תרבות",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "שירותים ממלכתיים - תרבות",
            "שירותים ממלכתיים: תרבות",
        ],
    },
    # ── BUDGET – LOANS ───────────────────────────────────────────────────────
    {
        "code": "BUDGET_LOANS",
        "name_he": "מלוות",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "מלוות",
        ],
    },
    {
        "code": "BUDGET_LOANS_REFINANCE",
        "name_he": "מלוות למחזור ולאיזון",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "מלוות למחזור ולאיזון",
        ],
    },
    {
        "code": "BUDGET_LOANS_REPAYMENT",
        "name_he": "פירעון מלוות",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הוצאות לפירעון מלוות",
        ],
    },
    # ── BUDGET – TOTALS ──────────────────────────────────────────────────────
    {
        "code": "BUDGET_TOTAL_RECEIPTS",
        "name_he": "סה\"כ תקבולים (רגיל + בלתי רגיל)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תקבולים | סה\"כ תקבולים (תקציב רגיל ותקציב בלתי רגיל)",
        ],
    },
    {
        "code": "BUDGET_TOTAL_PAYMENTS",
        "name_he": "סה\"כ תשלומים (רגיל + בלתי רגיל)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תשלומים | סה\"כ תשלומים (תקציב רגיל ותקציב בלתי רגיל)",
        ],
    },
    {
        "code": "BUDGET_EXTRA_EXPENSES_TOTAL",
        "name_he": "הוצאות בלתי רגילות (סה\"כ)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ הוצאות בתקציב בלתי רגיל",
        ],
    },
    {
        "code": "BUDGET_EXTRA_INCOME_TOTAL",
        "name_he": "הכנסות בלתי רגילות (סה\"כ)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "סה\"כ הכנסות בתקציב בלתי רגיל",
        ],
    },
    {
        "code": "BUDGET_ADMIN",
        "name_he": "הנהלה וכלליות",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "הנהלה וכלליות",
        ],
    },
    {
        "code": "BUDGET_OPERATIONAL_EXPENSES",
        "name_he": "הוצאות תפעול (תקציב רגיל)",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "תשלומים בתקציב הרגיל - לפי סוג ההוצאה | הוצאות תפעול",
        ],
    },
    # ── PROPERTY TAX BY TYPE ─────────────────────────────────────────────────
    {
        "code": "TAX_COMMERCE",
        "name_he": "ארנונה – משרדים ומסחר",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "למשרדים, שירותים ומסחר",
        ],
    },
    {
        "code": "TAX_HOTELS",
        "name_he": "ארנונה – בתי מלון",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "לבתי מלון",
        ],
    },
    {
        "code": "TAX_AGRI_LAND",
        "name_he": "ארנונה – קרקע חקלאית",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "לאדמה חקלאית",
        ],
    },
    {
        "code": "TAX_SOLAR",
        "name_he": "ארנונה – מערכות סולריות",
        "domain": "budget",
        "unit": "אלפי ש\"ח",
        "is_percentage": False,
        "higher_is_better": None,
        "cbs_column_variants": [
            "למערכת סולרית על גג נכס",
            "למערכת סולרית שאינה על גג נכס",
            "לקרקע תפוסה למערכת סולרית",
        ],
    },
]


def main():
    with open(SEED_PATH, encoding="utf-8") as f:
        existing = json.load(f)

    existing_codes = {ind["code"] for ind in existing}
    added = []
    for ind in NEW_INDICATORS:
        if ind["code"] not in existing_codes:
            existing.append(ind)
            added.append(ind["code"])
        else:
            print(f"  skip (already exists): {ind['code']}")

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {len(added)} new indicators:")
    for c in added:
        print(f"  + {c}")
    print(f"\nTotal indicators in file: {len(existing)}")


if __name__ == "__main__":
    main()
