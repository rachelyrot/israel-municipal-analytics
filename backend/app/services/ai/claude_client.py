import httpx
import anthropic
from app.config import settings

SYSTEM_PROMPT = """אתה אנליסט נתונים של רשויות מקומיות בישראל.
כלל ברזל: ענה אך ורק על בסיס הנתונים שסופקו ב-context. אל תמציא מספרים.
אם הנתון אינו בcontext — כתוב "הנתון אינו זמין".
ענה בעברית, בקצרה ובדיוק. כשמצטט ערך — ציין את שנת המדידה."""

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
