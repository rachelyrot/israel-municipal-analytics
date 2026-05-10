"""
Populates lat/lon for all municipalities using Nominatim (OpenStreetMap).
Run once after seeding municipalities:
    python scripts/seed_coordinates.py
Respects Nominatim rate limit: 1 req/sec.
"""
import sys
import time
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import requests
from app.database import SessionLocal
from app.models.municipality import Municipality

NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "IsraeliMunicipalAnalytics/1.0"}

# Hardcoded coordinates for problematic or ambiguous names
OVERRIDES: dict[str, tuple[float, float]] = {
    "ירושלים": (31.7683, 35.2137),
    "תל אביב-יפו": (32.0853, 34.7818),
    "חיפה": (32.7940, 34.9896),
    "ראשון לציון": (31.9730, 34.7925),
    "פתח תקווה": (32.0869, 34.8878),
    "אשדוד": (31.8044, 34.6553),
    "נתניה": (32.3215, 34.8532),
    "באר שבע": (31.2518, 34.7913),
    "בני ברק": (32.0847, 34.8338),
    "רמת גן": (32.0682, 34.8239),
    "אשקלון": (31.6688, 34.5742),
    "חולון": (32.0114, 34.7739),
    "בת ים": (32.0235, 34.7504),
    "הרצליה": (32.1664, 34.8439),
    "כפר סבא": (32.1747, 34.9077),
    "רעננה": (32.1841, 34.8709),
    "מודיעין-מכבים-רעות": (31.8982, 35.0103),
    "לוד": (31.9519, 34.8961),
    "רמלה": (31.9264, 34.8738),
    "נצרת": (32.7021, 35.2978),
    "עכו": (32.9233, 35.0715),
    "אילת": (29.5577, 34.9519),
    "טבריה": (32.7922, 35.5312),
    "צפת": (32.9646, 35.4961),
    "דימונה": (31.0695, 35.0311),
    "אופקים": (31.3113, 34.6208),
    "נהריה": (33.0043, 35.0989),
    "קריית שמונה": (33.2077, 35.5699),
    "בית שאן": (32.5022, 35.5028),
    "יוקנעם עילית": (32.6550, 35.1057),
    "מגדל העמק": (32.6778, 35.2386),
    "עפולה": (32.6078, 35.2895),
    "חדרה": (32.4367, 34.9192),
    "זכרון יעקב": (32.5700, 34.9553),
    "בנימינה-גבעת עדה": (32.5215, 34.9487),
    "טירת כרמל": (32.7603, 34.9693),
    "קריית ביאליק": (32.8437, 35.0818),
    "קריית ים": (32.8511, 35.0683),
    "קריית מוצקין": (32.8367, 35.0741),
    "קריית אתא": (32.8072, 35.1098),
    "קריית גת": (31.6068, 34.7644),
    "קריית מלאכי": (31.7291, 34.7418),
    "שדרות": (31.5260, 34.5960),
    "ערד": (31.2582, 35.2127),
    "מצפה רמון": (30.6102, 34.8013),
    "גבעתיים": (32.0738, 34.8117),
    "רחובות": (31.8928, 34.8113),
    "נס ציונה": (31.9302, 34.7995),
    "יבנה": (31.8765, 34.7427),
    "אור יהודה": (32.0297, 34.8563),
    "גבעת שמואל": (32.0800, 34.8467),
    "קריית אונו": (32.0612, 34.8607),
    "אלעד": (32.0520, 34.9501),
    "רמת השרון": (32.1475, 34.8394),
    "כפר יונה": (32.3151, 34.9374),
    "טייבה": (32.2691, 35.0038),
    "אום אל-פחם": (32.5237, 35.1530),
    "נצרת עילית": (32.7068, 35.3327),
    "שפרעם": (32.8067, 35.1709),
    "סחנין": (32.8554, 35.2023),
    "ג'לג'וליה": (32.1538, 34.9560),
    "כפר קאסם": (32.1146, 34.9760),
    "ראש העין": (32.0952, 34.9552),
    "בית שמש": (31.7466, 34.9939),
    "מעלה אדומים": (31.7732, 35.2975),
    "אריאל": (32.1060, 35.1677),
    "ביתר עילית": (31.6941, 35.1205),
    "מודיעין עילית": (31.9326, 35.0463),
    "אבו גוש": (31.8059, 35.1124),
    "מזכרת בתיה": (31.8543, 34.8456),
    "גדרה": (31.8106, 34.7789),
    "גן יבנה": (31.7933, 34.7125),
    "קסייפה": (31.2611, 35.1413),
    "רהט": (31.3932, 34.7544),
    "לקיה": (31.3612, 34.8199),
    "עומר": (31.2701, 34.8460),
    "מיתר": (31.3397, 34.9255),
    "ירוחם": (30.9872, 34.9310),
    "נתיבות": (31.4193, 34.5912),
    "גבעת ברנר": (31.8689, 34.7918),
    "גן שמואל": (32.4641, 34.9434),
    "פרדס חנה-כרכור": (32.4738, 34.9699),
    "זמר": (32.3513, 35.0191),
    "ג'סר א-זרקא": (32.5375, 34.9101),
    "בועינה-נוג'ידאת": (32.8137, 35.3448),
    "כפר מנדא": (32.8174, 35.2561),
    "ערערה": (32.4973, 35.0907),
}


def geocode(name: str) -> tuple[float, float] | None:
    params = {
        "q": f"{name}, ישראל",
        "format": "json",
        "limit": 1,
        "countrycodes": "il",
    }
    try:
        r = requests.get(NOMINATIM, params=params, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  Geocode error for {name}: {e}")
    return None


def main():
    db = SessionLocal()
    munis = db.query(Municipality).filter(Municipality.lat.is_(None)).all()
    print(f"Municipalities without coordinates: {len(munis)}")

    updated = 0
    for muni in munis:
        # Check override first
        if muni.name in OVERRIDES:
            lat, lon = OVERRIDES[muni.name]
            muni.lat = lat
            muni.lon = lon
            db.commit()
            updated += 1
            print(f"  [override] {muni.name}: {lat}, {lon}")
            continue

        # Try each alias too
        coords = None
        for name in [muni.name] + (muni.name_aliases or []):
            coords = geocode(name)
            if coords:
                break
            time.sleep(1)

        if coords:
            muni.lat, muni.lon = coords
            db.commit()
            updated += 1
            print(f"  [nominatim] {muni.name}: {muni.lat:.4f}, {muni.lon:.4f}")
        else:
            print(f"  [SKIP] {muni.name}: no coordinates found")

        time.sleep(1)  # Nominatim rate limit: 1 req/sec

    db.close()
    print(f"\nDone. Updated {updated}/{len(munis)} municipalities.")


if __name__ == "__main__":
    main()
