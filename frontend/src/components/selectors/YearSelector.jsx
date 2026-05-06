import { useDashboardStore } from '../../store/dashboardStore'

const YEARS = Array.from({ length: 26 }, (_, i) => 2024 - i)

export function YearSelector() {
  const { selectedYear, setYear } = useDashboardStore()

  return (
    <select
      value={selectedYear}
      onChange={e => setYear(Number(e.target.value))}
      className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-sm shadow-sm outline-none cursor-pointer"
      dir="rtl"
    >
      {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
    </select>
  )
}
