# שלב 4 — AI בעברית
## תת-שלבים מפורטים

---

### 4.1 — claude_client.py (Backend)

> ✅ הושלם — 2026-05-07 — anthropic==0.55.0 הותקן, claude_client.py נוצר, import תקין

**מה עושים:** הגדרת לקוח Anthropic עם prompt caching על system prompt קבוע

**התקנה:**
```bash
# מתוך backend/ עם venv פעיל
pip install anthropic
```
הוסף ל-`backend/requirements.txt`:
```
anthropic==0.55.0
```

הוסף ל-`backend/app/config.py`:
```python
anthropic_api_key: str = ""  # ANTHROPIC_API_KEY ב-.env
```

**`backend/app/services/ai/__init__.py`** — ריק

**`backend/app/services/ai/claude_client.py`:**
```python
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
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
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
                "cache_control": {"type": "ephemeral"},  # prompt caching על system
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
```

**אימות:** `python -c "from app.services.ai.claude_client import chat; print(chat('מה האוכלוסייה?', 'תל אביב 2022: אוכלוסייה 474000'))"` → תשובה עברית

---

### 4.2 — context_builder.py (Backend)

> ✅ הושלם — 2026-05-07 — context_builder.py נוצר, תל אביב 2022 מחזיר 91 מקורות + טבלה עברית

**מה עושים:** שליפת נתוני רשות מה-DB ועיצובם כטבלה עברית ל-Claude

**`backend/app/services/ai/context_builder.py`:**
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.municipality import Municipality
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage


def build_municipality_context(db: Session, municipality_id: int, year: int) -> tuple[str, list[dict]]:
    """
    מחזיר (context_text, sources_list).
    context_text — טבלה עברית מובנית לשליחה ל-Claude.
    sources_list — רשימת מקורות לציטוט בתשובה.
    [{ "indicator_code", "name_he", "value", "unit", "year", "national_avg" }]
    """
    muni = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not muni:
        return "רשות לא נמצאה.", []

    # שלוף כל data_points לשנה הנבחרת
    data_points = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(
            and_(DataPoint.municipality_id == municipality_id, DataPoint.year == year)
        )
        .order_by(Indicator.domain, Indicator.name_he)
        .all()
    )

    if not data_points:
        return f"אין נתונים עבור {muni.name} לשנת {year}.", []

    lines = [f"רשות: {muni.name} | שנה: {year} | סוג: {muni.municipality_type or 'לא ידוע'} | מחוז: {muni.district or 'לא ידוע'}"]
    lines.append(f"אשכול חברתי-כלכלי: {muni.socioeconomic_cluster or 'לא ידוע'}")
    lines.append("")
    lines.append("תחום | מדד | ערך | יחידה | ממוצע ארצי")
    lines.append("-" * 60)

    sources = []
    current_domain = None
    for dp, ind, na in data_points:
        if dp.value is None:
            continue
        domain = ind.domain or "כללי"
        if domain != current_domain:
            lines.append(f"\n[{domain}]")
            current_domain = domain
        avg_str = f"{na.avg_value:,.1f}" if na and na.avg_value else "אין נתון"
        lines.append(f"  {ind.name_he} | {dp.value:,.2f} | {ind.unit or ''} | ממוצע ארצי: {avg_str}")
        sources.append({
            "indicator_code": ind.code,
            "name_he": ind.name_he,
            "value": dp.value,
            "unit": ind.unit,
            "year": year,
            "national_avg": na.avg_value if na else None,
        })

    return "\n".join(lines), sources
```

**אימות:** `python -c "from app.database import SessionLocal; from app.services.ai.context_builder import build_municipality_context; db=SessionLocal(); ctx,src=build_municipality_context(db,504,2022); print(ctx[:500])"` → טבלה עברית מובנית

---

### 4.3 — query_engine.py (Backend)

> ✅ הושלם — 2026-05-07 — query_engine.py נוצר, import תקין

**מה עושים:** שאלה חופשית → שליפת נתונים → context → Claude → תשובה + מקורות

**`backend/app/services/ai/query_engine.py`:**
```python
import uuid
from sqlalchemy.orm import Session

from app.services.ai import claude_client, context_builder


def answer_question(
    db: Session,
    question: str,
    municipality_id: int,
    year: int,
    session_id: str | None = None,
) -> dict:
    """
    Returns:
    {
      "answer": "...",
      "sources": [{ "indicator_code", "name_he", "value", "unit", "year", "national_avg" }],
      "session_id": "uuid",
      "municipality_id": int,
      "year": int,
    }
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    context, sources = context_builder.build_municipality_context(db, municipality_id, year)

    if not sources:
        return {
            "answer": f"אין נתונים זמינים לרשות זו לשנת {year}.",
            "sources": [],
            "session_id": session_id,
            "municipality_id": municipality_id,
            "year": year,
        }

    answer = claude_client.chat(question, context)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id,
        "municipality_id": municipality_id,
        "year": year,
    }
```

**אימות:** `python -c "from app.database import SessionLocal; from app.services.ai.query_engine import answer_question; db=SessionLocal(); r=answer_question(db,'מה שיעור התעסוקה?',504,2022); print(r['answer'])"` → תשובה עברית מבוססת נתונים

---

### 4.4 — insight_generator.py (Backend)

> ✅ הושלם — 2026-05-07 — insight_generator.py נוצר, import תקין

**מה עושים:** Python מזהה חריגות ומגמות, Claude מנסח אותן בעברית

**`backend/app/services/ai/insight_generator.py`:**
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.models.national_average import NationalAverage
from app.services.ai import claude_client


def generate_insights(db: Session, municipality_id: int, year: int) -> list[str]:
    """
    מחזיר רשימה של עד 4 תובנות עבריות על הרשות.
    Python מחשב מה מעניין, Claude מנסח בלבד.
    """
    rows = (
        db.query(DataPoint, Indicator, NationalAverage)
        .join(Indicator, DataPoint.indicator_id == Indicator.id)
        .outerjoin(
            NationalAverage,
            and_(
                NationalAverage.indicator_id == Indicator.id,
                NationalAverage.year == year,
            ),
        )
        .filter(
            and_(DataPoint.municipality_id == municipality_id, DataPoint.year == year)
        )
        .all()
    )

    findings = []

    for dp, ind, na in rows:
        if dp.value is None or na is None or na.avg_value is None or na.avg_value == 0:
            continue
        deviation_pct = (dp.value - na.avg_value) / na.avg_value * 100
        if abs(deviation_pct) >= 30:  # חריגה משמעותית מהממוצע הארצי
            direction = "גבוה" if deviation_pct > 0 else "נמוך"
            findings.append(
                f"{ind.name_he}: {dp.value:,.1f} {ind.unit or ''} — "
                f"{abs(deviation_pct):.0f}% {direction} מהממוצע הארצי ({na.avg_value:,.1f})"
            )

    if not findings:
        return []

    # Claude מנסח כל ממצא כמשפט עברי קצר
    findings_text = "\n".join(f"- {f}" for f in findings[:6])
    prompt = f"""הנה ממצאים סטטיסטיים על רשות מקומית לשנת {year}:
{findings_text}

נסח כל ממצא כמשפט עברי קצר ובהיר (משפט אחד לממצא). אל תוסיף מידע שלא מופיע כאן."""

    raw = claude_client.chat(prompt, findings_text)
    insights = [line.lstrip("•- ").strip() for line in raw.splitlines() if line.strip()]
    return insights[:4]
```

**אימות:** `python -c "from app.database import SessionLocal; from app.services.ai.insight_generator import generate_insights; db=SessionLocal(); print(generate_insights(db,504,2022))"` → רשימת 1–4 משפטים עבריים

---

### 4.5 — AI Router (Backend)

> ✅ הושלם — 2026-05-07 — routers/ai.py נוצר, main.py עודכן, /api/v1/ai/query + /api/v1/ai/insights/{id} רשומים (21 routes סה"כ)

**מה עושים:** חיבור שירותי ה-AI ל-API

**`backend/app/routers/ai.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai import query_engine, insight_generator

router = APIRouter(prefix="/ai", tags=["ai"])


class QueryRequest(BaseModel):
    question: str
    municipality_id: int
    year: int = 2022
    session_id: str | None = None


@router.post("/query")
def query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    שאלה חופשית בעברית על רשות מקומית.
    POST /api/v1/ai/query
    Body: { "question": "מה שיעור הבגרות?", "municipality_id": 504, "year": 2022 }
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    return query_engine.answer_question(
        db, req.question, req.municipality_id, req.year, req.session_id
    )


@router.get("/insights/{municipality_id}")
def insights(municipality_id: int, year: int = 2022, db: Session = Depends(get_db)):
    """
    תובנות אוטומטיות על רשות ושנה.
    GET /api/v1/ai/insights/504?year=2022
    """
    result = insight_generator.generate_insights(db, municipality_id, year)
    return {"municipality_id": municipality_id, "year": year, "insights": result}
```

**עדכון `backend/app/main.py`:**
```python
from app.routers import municipalities, indicators, data, admin, analytics, ai
# ...
app.include_router(ai.router, prefix="/api/v1")
```

**אימות:**
```bash
curl -X POST localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"question":"מה האוכלוסייה?","municipality_id":504,"year":2022}'
# → { "answer": "...", "sources": [...] }

curl "localhost:8000/api/v1/ai/insights/504?year=2022"
# → { "insights": ["...", "..."] }
```

---

### 4.6 — AIQueryPage.jsx + Navbar (Frontend)

> ✅ הושלם — 2026-05-07 — AIQueryPage.jsx נוצר, route /ai + כפתור navbar הוספו, npm run build עבר (599 modules)

**מה עושים:** דף שאלות AI — בחירת רשות + שנה + שאלה חופשית + תשובה + מקורות

**הוסף ל-`frontend/src/api/client.js`:**
```js
getSimilar: (municipalityId, year) =>
  get(`/analytics/similar/${municipalityId}?year=${year}`),

aiQuery: (question, municipalityId, year, sessionId = null) =>
  fetch('/api/v1/ai/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, municipality_id: municipalityId, year, session_id: sessionId }),
  }).then(r => { if (!r.ok) throw new Error(r.status); return r.json() }),

getInsights: (municipalityId, year) =>
  get(`/ai/insights/${municipalityId}?year=${year}`),
```

**`frontend/src/pages/AIQueryPage.jsx`:**
```jsx
import { useState, useEffect, useRef } from 'react'
import { MunicipalitySelector } from '../components/selectors/MunicipalitySelector'
import { YearSelector } from '../components/selectors/YearSelector'
import { api } from '../api/client'

export function AIQueryPage() {
  const [muni, setMuni] = useState(null)
  const [year, setYear] = useState(2022)
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [insights, setInsights] = useState([])
  const sessionId = useRef(crypto.randomUUID())

  useEffect(() => {
    if (!muni) return
    setInsights([])
    api.getInsights(muni.id, year).then(r => setInsights(r.insights || []))
  }, [muni, year])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!muni || !question.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const r = await api.aiQuery(question, muni.id, year, sessionId.current)
      setResult(r)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto" dir="rtl">
      <h1 className="text-2xl font-bold mb-6">שאל על רשות מקומית</h1>

      {/* בחירת רשות + שנה */}
      <div className="bg-white rounded-xl shadow p-4 flex gap-4 flex-wrap items-end mb-6">
        <div className="flex-1 min-w-48">
          <label className="text-sm text-gray-500 block mb-1">רשות</label>
          <MunicipalitySelector value={muni} onChange={setMuni} />
        </div>
        <div>
          <label className="text-sm text-gray-500 block mb-1">שנה</label>
          <YearSelector value={year} onChange={setYear} />
        </div>
      </div>

      {/* תובנות אוטומטיות */}
      {insights.length > 0 && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <h3 className="font-semibold text-blue-800 mb-2 text-sm">תובנות אוטומטיות</h3>
          <ul className="space-y-1">
            {insights.map((ins, i) => (
              <li key={i} className="text-sm text-blue-900">• {ins}</li>
            ))}
          </ul>
        </div>
      )}

      {/* שאלה */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-4 mb-6">
        <label className="text-sm text-gray-500 block mb-2">שאל שאלה חופשית</label>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="לדוגמה: מה שיעור הבגרות לעומת הממוצע הארצי?"
            className="flex-1 border rounded-lg px-3 py-2 text-sm"
            disabled={!muni}
          />
          <button
            type="submit"
            disabled={loading || !muni || !question.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-40"
          >
            {loading ? 'שולח...' : 'שלח'}
          </button>
        </div>
      </form>

      {/* תשובה */}
      {result && (
        <div className="bg-white rounded-xl shadow p-6">
          <p className="text-gray-900 leading-relaxed mb-4 whitespace-pre-wrap">{result.answer}</p>
          {result.sources?.length > 0 && (
            <details className="mt-4">
              <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">
                מקורות ({result.sources.length} מדדים)
              </summary>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {result.sources.map((s, i) => (
                  <div key={i} className="text-xs text-gray-500 bg-gray-50 rounded px-2 py-1">
                    <span className="font-medium text-gray-700">{s.name_he}</span>:{' '}
                    {s.value?.toLocaleString('he-IL')} {s.unit}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      )}
    </div>
  )
}
```

**עדכון `frontend/src/App.jsx`:**
```jsx
import { AIQueryPage } from './pages/AIQueryPage'

// בnavbar:
<NavLink to="/ai" className={({ isActive }) => isActive ? active : inactive}>AI</NavLink>

// בRoutes:
<Route path="/ai" element={<AIQueryPage />} />
```

**אימות:** בחר "תל אביב-יפו" 2022 → תובנות אוטומטיות מופיעות → הקלד "מה שיעור התעסוקה?" → תשובה עברית עם מקורות

---

## סיכום שלב 4

| תת-שלב | קובץ עיקרי | אימות | סטטוס |
|--------|-----------|-------|--------|
| 4.1 | `services/ai/claude_client.py` | `chat("שאלה","context")` → תשובה עברית | ✅ |
| 4.2 | `services/ai/context_builder.py` | `build_municipality_context(db,504,2022)` → טבלה | ✅ |
| 4.3 | `services/ai/query_engine.py` | `answer_question(db,"...",504,2022)` → `{answer,sources}` | ✅ |
| 4.4 | `services/ai/insight_generator.py` | `generate_insights(db,504,2022)` → רשימת משפטים | ✅ |
| 4.5 | `routers/ai.py` + עדכון main.py | `POST /api/v1/ai/query` → 200 OK | ✅ |
| 4.6 | `AIQueryPage.jsx` + עדכון App.jsx | בחר רשות → תובנות + שאלה → תשובה | ✅ |

**סדר ביצוע מומלץ:** 4.1 → 4.2 → 4.3 → 4.4 → 4.5 (backend רץ + API עובד) → 4.6 (frontend)

**דרישות מוקדמות:**
- `ANTHROPIC_API_KEY` ב-`backend/.env`
- `pip install anthropic` (הוסף ל-requirements.txt)
