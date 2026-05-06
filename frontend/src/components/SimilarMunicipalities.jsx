import { useState, useEffect } from 'react'
import { api } from '../api/client'
import { useDashboardStore } from '../store/dashboardStore'

export function SimilarMunicipalities() {
  const { selectedMunicipality, selectedYear, setMunicipality } = useDashboardStore()
  const [similar, setSimilar] = useState([])

  useEffect(() => {
    if (!selectedMunicipality) {
      setSimilar([])
      return
    }
    api.getSimilar(selectedMunicipality.id, selectedYear).then(setSimilar).catch(() => setSimilar([]))
  }, [selectedMunicipality, selectedYear])

  if (!selectedMunicipality || similar.length === 0) return null

  return (
    <div className="bg-white rounded-xl shadow p-4" dir="rtl">
      <h3 className="font-semibold text-gray-700 mb-3">רשויות דומות</h3>
      <div className="flex flex-col gap-2">
        {similar.slice(0, 5).map(m => (
          <button
            key={m.id}
            onClick={() => setMunicipality(m)}
            className="flex items-center justify-between text-sm px-3 py-2 rounded-lg hover:bg-blue-50 text-right transition"
          >
            <span className="font-medium text-gray-800">{m.name}</span>
            <span className="text-xs text-gray-400">
              {m.district} · {(m.similarity_score * 100).toFixed(0)}% דמיון
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
