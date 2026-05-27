import { create } from 'zustand'
import { api } from '../api/client'

export const useDashboardStore = create((set, get) => ({
  selectedMunicipality: null,
  selectedYear: 2020,
  selectedDomain: null,
  filterDistrict: null,
  filterType: null,
  hideRegional: false,
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

  setFilterDistrict: (district) => set({ filterDistrict: district }),
  setFilterType: (type) => set({ filterType: type }),
  setHideRegional: (hide) => set({ hideRegional: hide }),

  fetchKPIs: async () => {
    const { selectedMunicipality, selectedYear } = get()
    if (!selectedMunicipality) return
    set({ isLoadingKPIs: true, error: null })
    try {
      const kpis = await api.getKPIs(selectedMunicipality.id, selectedYear)
      set({ kpis, isLoadingKPIs: false })
    } catch (e) {
      set({ error: e.message, isLoadingKPIs: false })
    }
  },
}))
