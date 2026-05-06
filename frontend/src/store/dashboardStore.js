import { create } from 'zustand'
import { api } from '../api/client'

export const useDashboardStore = create((set, get) => ({
  selectedMunicipality: null,
  selectedYear: 2020,
  selectedDomain: null,
  kpis: [],
  isLoadingKPIs: false,
  error: null,

  setMunicipality: (municipality) => {
    set({ selectedMunicipality: municipality, kpis: [] })
    if (municipality) get().fetchKPIs()
  },

  setYear: (year) => {
    set({ selectedYear: year })
    if (get().selectedMunicipality) get().fetchKPIs()
  },

  setDomain: (domain) => {
    set({ selectedDomain: domain })
    if (get().selectedMunicipality) get().fetchKPIs()
  },

  fetchKPIs: async () => {
    const { selectedMunicipality, selectedYear, selectedDomain } = get()
    if (!selectedMunicipality) return
    set({ isLoadingKPIs: true, error: null })
    try {
      const kpis = await api.getKPIs(selectedMunicipality.id, selectedYear, selectedDomain)
      set({ kpis, isLoadingKPIs: false })
    } catch (e) {
      set({ error: e.message, isLoadingKPIs: false })
    }
  },
}))
