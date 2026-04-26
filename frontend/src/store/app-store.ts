import { create } from 'zustand'
import type { NavView } from '../types/platform'

interface AppState {
  activeView: NavView
  sidebarExpanded: boolean
  mobileDrawerOpen: boolean
  mobileMarketingNavOpen: boolean
  setActiveView: (view: NavView) => void
  toggleSidebar: () => void
  setMobileDrawerOpen: (open: boolean) => void
  setMobileMarketingNavOpen: (open: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  activeView: 'dashboard',
  sidebarExpanded: true,
  mobileDrawerOpen: false,
  mobileMarketingNavOpen: false,
  setActiveView: (activeView: NavView) => set({ activeView }),
  toggleSidebar: () => set((state) => ({ sidebarExpanded: !state.sidebarExpanded })),
  setMobileDrawerOpen: (mobileDrawerOpen: boolean) => set({ mobileDrawerOpen }),
  setMobileMarketingNavOpen: (mobileMarketingNavOpen: boolean) => set({ mobileMarketingNavOpen }),
}))
