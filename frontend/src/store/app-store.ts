import { create } from 'zustand'
import type { NavView } from '../types/platform'

interface AppState {
  activeView: NavView
  sidebarExpanded: boolean
  setActiveView: (view: NavView) => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  activeView: 'dashboard',
  sidebarExpanded: true,
  setActiveView: (activeView: NavView) => set({ activeView }),
  toggleSidebar: () => set((state) => ({ sidebarExpanded: !state.sidebarExpanded })),
}))
