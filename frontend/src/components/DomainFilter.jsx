import { useDashboardStore } from '../store/dashboardStore'

const DOMAINS = [
  { key: null,           label: 'הכל' },
  { key: 'population',  label: 'אוכלוסייה' },
  { key: 'education',   label: 'חינוך' },
  { key: 'employment',  label: 'תעסוקה' },
  { key: 'budget',      label: 'תקציב' },
  { key: 'welfare',     label: 'רווחה' },
  { key: 'taxes',       label: 'ארנונה' },
  { key: 'infrastructure', label: 'תשתיות' },
]

export function DomainFilter() {
  const { selectedDomain, setDomain } = useDashboardStore()

  return (
    <div className="flex gap-2 flex-wrap" dir="rtl">
      {DOMAINS.map(d => (
        <button
          key={d.key ?? 'all'}
          onClick={() => setDomain(d.key)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all
            ${selectedDomain === d.key
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
        >
          {d.label}
        </button>
      ))}
    </div>
  )
}
