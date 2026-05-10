import { useNavigate } from 'react-router-dom'

export function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-950 via-blue-800 to-blue-600 flex flex-col items-center justify-center text-white" dir="rtl">

      {/* Logo / icon */}
      <div className="text-8xl mb-6 select-none">🏙️</div>

      {/* Title */}
      <h1 className="text-5xl font-bold mb-3 text-center leading-tight">
        ניתוח רשויות מקומיות
      </h1>
      <p className="text-blue-200 text-xl mb-2 text-center">
        נתוני הלמ"ס 1999–2024
      </p>

      {/* Stats row */}
      <div className="flex gap-10 my-10 text-center">
        <div>
          <div className="text-4xl font-bold">256</div>
          <div className="text-blue-300 text-sm mt-1">רשויות מקומיות</div>
        </div>
        <div className="border-r border-blue-500" />
        <div>
          <div className="text-4xl font-bold">26</div>
          <div className="text-blue-300 text-sm mt-1">שנות נתונים</div>
        </div>
        <div className="border-r border-blue-500" />
        <div>
          <div className="text-4xl font-bold">60+</div>
          <div className="text-blue-300 text-sm mt-1">מדדים סטטיסטיים</div>
        </div>
      </div>

      {/* Features */}
      <div className="flex gap-6 mb-12 flex-wrap justify-center max-w-2xl">
        {[
          { icon: '📊', label: 'דשבורד KPIs' },
          { icon: '⚖️', label: 'השוואת רשויות' },
          { icon: '🗺️', label: 'מפה כורופלת' },
          { icon: '🤖', label: 'שאלות AI בעברית' },
        ].map(({ icon, label }) => (
          <div key={label} className="flex items-center gap-2 bg-white/10 rounded-full px-4 py-2 text-sm backdrop-blur">
            <span>{icon}</span>
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* CTA */}
      <button
        onClick={() => navigate('/app')}
        className="bg-white text-blue-800 font-bold text-lg px-10 py-4 rounded-2xl shadow-xl hover:bg-blue-50 hover:scale-105 active:scale-95 transition-all duration-150"
      >
        כניסה למערכת ←
      </button>

      {/* Footer */}
      <p className="mt-10 text-blue-400 text-xs">
        נתונים: הלשכה המרכזית לסטטיסטיקה (הלמ"ס)
      </p>
    </div>
  )
}
