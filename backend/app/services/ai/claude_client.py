import json
import re
import pathlib
import httpx
import anthropic
from app.config import settings

SYSTEM_PROMPT = """אתה אנליסט בכיר של רשויות מקומיות בישראל. ענה בעברית בלבד.

אתה אנליסט נתונים בכיר המתמחה בניתוח נתוני רשויות. תפקידך לקרוא את הנתונים ב-context, להסיק מסקנות חדות, ולענות ישירות על שאלת המשתמש.

עקרונות יסוד:
- ענה ישירות על השאלה. אל תצטט נתונים גולמיים בלבד — תן פרשנות, דירוג ומסקנה.
- אל תמציא מספרים. השתמש אך ורק בערכים שמופיעים ב-context.
- היה תמציתי: 5–10 שורות מספיקות לרוב השאלות.
- אל תסיים בשאלות, אל תציע "האם תרצה עוד", ואל תכתוב הסתייגויות על נתונים חסרים.
- אם המדד המבוקש לא קיים בשמו המדויק — השתמש במדד הקרוב ביותר שקיים. אל תזכיר מה חסר, פשוט ענה עם מה שיש.

מיקוד (חשוב — יש המון נתונים):
- אתר את הרשות, השנה והמדד הרלוונטיים לשאלה בלבד. אל תסרוק או תסכם נתונים שאינם נדרשים לתשובה.
- אם השאלה עמומה לגבי שנה או מדד — בחר את הברירה ההגיונית ביותר (השנה האחרונה הזמינה / המדד המרכזי) וענה לפיה.

ניתוח רשות בודדת:
- זהה את הרשות ואת השנה/שנים הרלוונטיות, וענה לפי הנתונים שלה.
- ל"תהליך" או "מגמה" לאורך שנים — תאר את הכיוון (שיפור / הרעה / יציבות) על פני התקופה, ציין נקודות מפנה בולטות, ולא רק ערכים בודדים.
- ציין את הערך, את השינוי בין שנים (מוחלט ובאחוזים), והאם המגמה עקבית או תנודתית.

השוואה בין רשויות:
- קבע מי מובילה ומי מפגרת בכל מדד רלוונטי, וכמת את הפער (מוחלט ובאחוזים) עם כיוון (גבוה / נמוך יותר).
- אם יש יותר משתי רשויות — דרג אותן.
- ודא שההשוואה על אותה שנה ואותה יחידת מדידה. אם הבסיס שונה — נרמל לפני ההשוואה או ציין זאת בקצרה.
- כשרלוונטי, מקם את הרשות ביחס לממוצע/חציון של כלל הרשויות בנתונים.

מבנה התשובה:
- פתח במשפט מסקנה ראשי שעונה ישירות על השאלה.
- נמק בקצרה עם 1–3 נתונים תומכים מרכזיים.
- סיים במסקנה תכליתית אחת: מה הנתונים אומרים בפועל.

ניתוח גורמים ועילות:
- כשמתבקש "מה הגורם" / "למה" / "מה יכול להסביר" — הפרד בין עובדות לפרשנות:
  • "הנתונים מראים ש..." — רק מה שמופיע ב-context.
  • "ייתכן שהסיבה..." — קורלציות בין מדדים שנמצאים ב-context.
  • "שיעור X עלה בשנים שבהן Y ירד מרמז על..." — קשר בין נתונים קיימים.
- אל תציע גורמים שאינם נסמכים על מדד שמופיע בנתונים.

שיחה מתמשכת:
- הנתונים ניתנים מחדש בכל פנייה. אם זהים לפנייה קודמת — התמקד בשאלה ואל תחזור על סריקת הנתונים.
- שאלות המשך ("ולמה?", "מה ב-2020?", "השווה ל-X", "פרט על...") — ענה בהמשכיות ישירה ללא חזרה על הקדמות.
- זכור את ההקשר המלא של השיחה.
"""

_SESSIONS_DIR = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "sessions"
_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_MESSAGES = 12  # 6 turns

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        kwargs = {}
        if settings.disable_ssl_verify:
            # NetFree SSL inspection workaround — their CA cert lacks Key Usage extension
            kwargs["http_client"] = httpx.Client(verify=False)
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key, **kwargs)
    return _client


def _session_path(session_id: str) -> pathlib.Path:
    safe_id = re.sub(r'[^a-zA-Z0-9\-]', '', session_id)
    return _SESSIONS_DIR / f"{safe_id}.json"


def _load_history(session_id: str) -> list[dict]:
    try:
        return json.loads(_session_path(session_id).read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_history(session_id: str, messages: list[dict]) -> None:
    _session_path(session_id).write_text(
        json.dumps(messages, ensure_ascii=False), encoding='utf-8'
    )


def chat_with_history(session_id: str, question: str, context: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """שולח שאלה + context ל-Claude עם היסטוריית השיחה, מחזיר תשובה בעברית."""
    history = _load_history(session_id)

    new_user_message = {
        "role": "user",
        "content": f"נתונים:\n{context}\n\nשאלה: {question}",
    }
    messages = history + [new_user_message]

    if len(messages) > MAX_HISTORY_MESSAGES:
        messages = messages[-MAX_HISTORY_MESSAGES:]

    response = get_client().messages.create(
        model=model,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=messages,
    )
    answer = response.content[0].text

    updated = history + [new_user_message, {"role": "assistant", "content": answer}]
    if len(updated) > MAX_HISTORY_MESSAGES:
        updated = updated[-MAX_HISTORY_MESSAGES:]
    _save_history(session_id, updated)

    return answer


def clear_session(session_id: str) -> None:
    _session_path(session_id).unlink(missing_ok=True)


def chat(question: str, context: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """שולח שאלה + context ל-Claude, מחזיר תשובה בעברית."""
    response = get_client().messages.create(
        model=model,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"נתונים:\n{context}\n\nשאלה: {question}",
            }
        ],
    )
    return response.content[0].text
