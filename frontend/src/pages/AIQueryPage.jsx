import { useState, useRef, useEffect } from 'react'
import { api } from '../api/client'

function UserBubble({ text }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-xl bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed">
        {text}
      </div>
    </div>
  )
}

function AssistantBubble({ text, sources, isError }) {
  return (
    <div className="flex justify-start">
      <div className={`max-w-2xl rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed shadow-sm ${
        isError
          ? 'bg-red-50 text-red-700 border border-red-100'
          : 'bg-white border border-slate-100 text-slate-800'
      }`}>
        <p className="whitespace-pre-wrap">{text}</p>
        {sources?.length > 0 && (
          <details className="mt-3">
            <summary className="text-xs text-slate-400 cursor-pointer hover:text-slate-600 select-none">
              מקורות ({sources.length} נקודות נתונים)
            </summary>
            <div className="mt-2 grid grid-cols-2 gap-1.5">
              {sources.slice(0, 24).map((s, i) => (
                <div key={i} className="text-xs text-slate-500 bg-slate-50 rounded px-2 py-1">
                  {s.municipality && (
                    <span className="text-blue-600 font-medium">{s.municipality} · </span>
                  )}
                  <span className="font-medium text-slate-700">{s.name_he}</span>
                  {s.year && <span className="text-slate-400"> ({s.year})</span>}:{' '}
                  {s.value?.toLocaleString('he-IL')} {s.unit}
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-4">
          {[0, 150, 300].map(delay => (
            <span
              key={delay}
              className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export function AIQueryPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const sessionId = useRef(crypto.randomUUID())
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const send = async (e) => {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: q }])
    setLoading(true)

    try {
      const r = await api.aiQuery(q, null, null, sessionId.current, null)
      setMessages(prev => [...prev, { role: 'assistant', text: r.answer, sources: r.sources }])
    } catch (err) {
      const msg = err?.detail || err?.message || 'שגיאה בשרת. נסה שוב.'
      setMessages(prev => [...prev, { role: 'assistant', text: msg, isError: true }])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  const clearChat = () => {
    api.clearSession(sessionId.current)
    sessionId.current = crypto.randomUUID()
    setMessages([])
    setInput('')
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50" dir="rtl">

      {/* Header */}
      <div className="bg-white border-b px-6 py-2.5 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-sm font-semibold text-slate-800">שאל AI</h1>
          <p className="text-xs text-slate-400">שאלות על נתוני רשויות מקומיות — השוואות, מגמות, גורמים</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-xs text-slate-400 hover:text-red-500 transition px-2 py-1 rounded hover:bg-red-50"
          >
            שיחה חדשה
          </button>
        )}
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 pt-16 select-none">
            <div className="text-4xl mb-3">💬</div>
            <p className="text-sm font-medium text-slate-500">שאל כל שאלה על רשויות מקומיות</p>
            <div className="mt-4 flex flex-col gap-2 items-center">
              {[
                'אלו רשויות הובילו בתעסוקה ב-2022?',
                'מה המגמה בשיעור הבגרות בין 2015 ל-2022?',
                'השווה תקציב לנפש בין ירושלים לתל אביב',
                'מה יכול להסביר ירידה בילודה בשנים האחרונות?',
              ].map(ex => (
                <button
                  key={ex}
                  onClick={() => { setInput(ex); inputRef.current?.focus() }}
                  className="text-xs text-blue-500 hover:text-blue-700 hover:underline"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) =>
          msg.role === 'user'
            ? <UserBubble key={i} text={msg.text} />
            : <AssistantBubble key={i} text={msg.text} sources={msg.sources} isError={msg.isError} />
        )}

        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="bg-white border-t px-4 py-3 flex-shrink-0">
        <form onSubmit={send} className="flex gap-2 max-w-3xl mx-auto">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) send(e) }}
            placeholder={loading ? 'מנתח...' : 'הקלד שאלה...'}
            className="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-50"
            autoFocus
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-40 transition whitespace-nowrap"
          >
            שלח
          </button>
        </form>
      </div>
    </div>
  )
}
