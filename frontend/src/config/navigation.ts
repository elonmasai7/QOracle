import type { NavView } from '../types/platform'

export const workspaceNavItems: Array<{ key: NavView; label: string; short: string }> = [
  { key: 'dashboard', label: 'Dashboard', short: 'DB' },
  { key: 'portfolios', label: 'Portfolios', short: 'PF' },
  { key: 'risk-engine', label: 'Risk Engine', short: 'RE' },
  { key: 'stress-testing', label: 'Stress Testing', short: 'ST' },
  { key: 'forecasting', label: 'Forecasting', short: 'FC' },
  { key: 'reports', label: 'Reports', short: 'RP' },
  { key: 'compliance', label: 'Compliance', short: 'CP' },
  { key: 'settings', label: 'Settings', short: 'SE' },
]

export const marketingNavItems = [
  { href: '#platform', label: 'Platform' },
  { href: '#solutions', label: 'Solutions' },
  { href: '#technology', label: 'Technology' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#resources', label: 'Resources' },
  { href: '#company', label: 'Company' },
]
