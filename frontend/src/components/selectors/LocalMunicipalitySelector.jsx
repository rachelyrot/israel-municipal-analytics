import { useState, useEffect, useRef } from 'react'
import { api } from '../../api/client'

/**
 * Controlled municipality selector — takes `value` (municipality object or null)
 * and `onChange` (callback receiving the selected municipality object).
 * Does NOT touch Zustand; safe to use multiple times on one page.
 */
export function LocalMunicipalitySelector({ value, onChange, placeholder = 'חפש רשות מקומית...' }) {
  const [query, setQuery] = useState(value ? value.name : '')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  // Keep input text in sync when value is cleared externally
  useEffect(() => {
    setQuery(value ? value.name : '')
  }, [value])

  useEffect(() => {
    if (query.length < 2) { setResults([]); setOpen(false); return }
    // If query matches the currently selected value's name, skip fetching
    if (value && query === value.name) return
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
    onChange(m)
    setQuery(m.name)
    setOpen(false)
  }

  const handleClear = () => {
    onChange(null)
    setQuery('')
    setResults([])
    setOpen(false)
  }

  return (
    <div ref={containerRef} className="relative w-72">
      <div className="flex items-center border border-gray-300 rounded-lg bg-white px-3 shadow-sm">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder}
          className="flex-1 py-2 outline-none text-sm text-right bg-transparent"
          dir="rtl"
        />
        {query && (
          <button onClick={handleClear} className="text-gray-400 hover:text-gray-600 text-lg leading-none mr-1">
            x
          </button>
        )}
        <span className="text-gray-400 text-sm ml-1">&#128269;</span>
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
