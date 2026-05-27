import { useDashboardStore } from '../store/dashboardStore'

const DISTRICTS = ['הכל', 'ירושלים', 'תל אביב', 'חיפה', 'המרכז', 'הדרום', 'הצפון', 'יהודה והשומרון']
const TYPES = [
  { label: 'הכל', value: null },
  { label: 'עירייה', value: 'עירייה' },
  { label: 'מועצה מקומית', value: 'מועצה מקומית' },
  { label: 'מועצה אזורית', value: 'מועצה אזורית' },
]
const YEARS = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

export function FilterBar({ filteredCount, totalCount = 257 }) {
  const {
    selectedYear, filterDistrict, filterType, hideRegional,
    setYear, setFilterDistrict, setFilterType, setHideRegional,
  } = useDashboardStore()

  const tab = (active) =>
    `px-2.5 py-1 text-xs rounded-full whitespace-nowrap cursor-pointer transition-colors select-none ${
      active ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'
    }`

  return (
    <div
      className="bg-white border-b px-4 py-2 flex items-center gap-3 flex-wrap flex-shrink-0"
      dir="rtl"
    >
      <span className="text-xs font-semibold text-gray-700">סינון משותף:</span>

      {/* מעמד */}
      <div className="flex items-center gap-1">
        {TYPES.map(({ label, value }) => (
          <button
            key={label}
            onClick={() => setFilterType(value)}
            className={tab(filterType === value)}
          >
            {label}
          </button>
        ))}
      </div>

      <span className="w-px h-4 bg-gray-200 flex-shrink-0" />

      {/* מחוז */}
      <div className="flex items-center gap-1 flex-wrap">
        {DISTRICTS.map(d => (
          <button
            key={d}
            onClick={() => setFilterDistrict(d === 'הכל' ? null : d)}
            className={tab(d === 'הכל' ? filterDistrict === null : filterDistrict === d)}
          >
            {d}
          </button>
        ))}
      </div>

      <span className="w-px h-4 bg-gray-200 flex-shrink-0" />

      {/* הסתר מועצות אזוריות */}
      <label className="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={hideRegional}
          onChange={e => setHideRegional(e.target.checked)}
          className="rounded border-gray-300 text-blue-600 cursor-pointer"
        />
        <span>הסתר מועצות אזוריות</span>
        <span className="text-gray-400">(מכוסות שישובים שונים)</span>
      </label>

      {/* counter — pushed to far right */}
      <span className="text-xs text-gray-500 mr-auto">
        {filteredCount ?? '—'} רשויות מתוך {totalCount}
      </span>

      <span className="w-px h-4 bg-gray-200 flex-shrink-0" />

      {/* שנה */}
      <div className="flex items-center gap-1.5">
        <span className="text-xs text-gray-500">שנה:</span>
        <select
          value={selectedYear}
          onChange={e => setYear(Number(e.target.value))}
          className="text-xs border border-gray-300 rounded-md px-2 py-1 bg-white cursor-pointer"
        >
          {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>
    </div>
  )
}
