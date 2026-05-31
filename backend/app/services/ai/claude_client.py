import httpx
import anthropic
from app.config import settings

SYSTEM_PROMPT = """אתה אנליסט בכיר של רשויות מקומיות בישראל. ענה בעברית בלבד.


כללי תשובה:
- קרא את הנתונים ב-context והסק מסקנות כמו אנליסט מנוסה. ענה ישירות על השאלה.
- אל תצטט נתונים גולמיים בלבד — תן פרשנות, דירוג ומסקנה.
- אם המדד המבוקש לא קיים בשמו המדויק — השתמש במדדים הקרובים ביותר שקיימים. אל תזכיר מה חסר, פשוט ענה עם מה שיש.
- אל תסיים בשאלות, אל תציע "האם תרצה עוד", ואל תכתוב הסתייגויות על נתונים חסרים.
- אל תמציא מספרים — השתמש רק בערכים שמופיעים ב-context.
- היה תמציתי: 5–10 שורות מספיקות לרוב השאלות.

השוואות בין נתונים:
- כשהשאלה כוללת השוואה (בין תקופות, ישויות, קטגוריות או מדדים) — זהה את הפריטים להשוואה והצג את ההפרש ביניהם.
- כמת את הפער: גם בערך מוחלט וגם באחוזים, כשרלוונטי. ציין כיוון (עלייה/ירידה, גבוה/נמוך יותר).
- קבע מי מוביל ומי מפגר, ודרג אם יש יותר משני פריטים.
- אם יש מגמה לאורך זמן — ציין אותה (גדל/קטן/יציב) ולא רק נקודות בודדות.
- בסס כל השוואה על ערכים שקיימים ב-context בלבד. אם בסיס ההשוואה שונה (יחידות/תקופות לא תואמות) — נרמל לפני ההשוואה או ציין זאת בקצרה.
- סיים במסקנה אחת: מה ההשוואה אומרת בפועל."""

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        # NetFree SSL inspection workaround — their CA cert lacks Key Usage extension
        _client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            http_client=httpx.Client(verify=False),
        )
    return _client


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
