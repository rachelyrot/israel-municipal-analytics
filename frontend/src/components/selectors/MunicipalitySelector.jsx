import { useState, useEffect, useRef, useCallback } from 'react'
import { api } from '../../api/client'
import { useDashboardStore } from '../../store/dashboardStore'

export function MunicipalitySelector() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const { selectedMunicipality, setMunicipality } = useDashboardStore()
  const containerRef = useRef(null)
  const skipSearch = useRef(false)

  // Sync input text when municipality is set externally (e.g. map click)
  useEffect(() => {
    skipSearch.current = true
    setQuery(selectedMunicipality ? selectedMunicipality.name : '')
    setOpen(false)
    setResults([])
  }, [selectedMunicipality?.id])

  useEffect(() => {
    if (skipSearch.current) { skipSearch.current = false; return }
    if (query.length < 2) { setResults([]); setOpen(false); return }
    const t = setTimeout(() =>
      api.searchMunicipalities(query)
        .then(data => { setResults(data); setOpen(data.length > 0) })
        .catch(() => {}),
      300
    )
    return () => clearTimeout(t)
  }, [query])

  useEffect(() => {
    function handleClick(e) {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleSelect = (m) => {
    setMunicipality(m)
    setQuery(m.name)
    setOpen(false)
  }

  const handleClear = () => {
    setMunicipality(null)
    setQuery('')
    setResults([])
  }

  return (
    <div ref={containerRef} className="relative w-72">
      <div className="flex items-center border border-gray-300 rounded-lg bg-white px-3 shadow-sm">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="חפש רשות מקומית..."
          className="flex-1 py-2 outline-none text-sm text-right bg-transparent"
          dir="rtl"
        />
        {query && (
          <button onClick={handleClear} className="text-gray-400 hover:text-gray-600 text-lg leading-none mr-1">
            ×
          </button>
        )}
        <span className="text-gray-400 text-sm">🔍</span>
      </div>
      {open && (
        <div className="absolute top-full mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-56 overflow-y-auto">
          {results.map(m => (
            <div
              key={m.id}
              onClick={() => handleSelect(m)}
              className="px-4 py-2.5 hover:bg-blue-50 cursor-pointer flex justify-between items-center"
              dir="rtl"
            >
              <span className="font-medium text-sm">{m.name}</span>
              <span className="text-xs text-gray-400">{m.municipality_type} · {m.district}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
