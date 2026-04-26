import { cn } from '../../lib/cn'
import { useAppStore } from '../../store/app-store'
import type { NavView } from '../../types/platform'

const navItems: Array<{ key: NavView; label: string; short: string }> = [
  { key: 'dashboard', label: 'Dashboard', short: 'DB' },
  { key: 'portfolios', label: 'Portfolios', short: 'PF' },
  { key: 'risk-engine', label: 'Risk Engine', short: 'RE' },
  { key: 'stress-testing', label: 'Stress Testing', short: 'ST' },
  { key: 'forecasting', label: 'Forecasting', short: 'FC' },
  { key: 'reports', label: 'Reports', short: 'RP' },
  { key: 'compliance', label: 'Compliance', short: 'CP' },
  { key: 'settings', label: 'Settings', short: 'SE' },
]

export function Sidebar() {
  const { activeView, setActiveView, sidebarExpanded, toggleSidebar } = useAppStore()

  return (
    <aside
      className={cn(
        'surface-panel sticky top-24 hidden h-[calc(100vh-7rem)] flex-col overflow-hidden px-3 py-4 lg:flex',
        sidebarExpanded ? 'w-[260px]' : 'w-[72px]',
      )}
    >
      <button
        type="button"
        onClick={toggleSidebar}
        className="mb-6 flex h-11 items-center rounded-xl border border-white/10 bg-white/5 px-3 text-left text-sm text-white transition hover:bg-white/8"
      >
        <span className="inline-flex size-8 items-center justify-center rounded-lg bg-qr-blue/20 text-xs font-semibold text-blue-300">
          QR
        </span>
        {sidebarExpanded ? <span className="ml-3 font-medium">Workspace</span> : null}
      </button>

      <nav className="space-y-1.5">
        {navItems.map((item) => {
          const active = item.key === activeView
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => setActiveView(item.key)}
              className={cn(
                'flex h-11 w-full items-center rounded-xl px-3 text-sm transition-all duration-150',
                active ? 'bg-blue-600/16 text-white shadow-[inset_0_0_0_1px_rgba(37,99,235,0.45)]' : 'text-slate-300 hover:bg-white/5 hover:text-white',
              )}
            >
              <span className="inline-flex size-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-[11px] font-semibold">
                {item.short}
              </span>
              {sidebarExpanded ? <span className="ml-3">{item.label}</span> : null}
            </button>
          )
        })}
      </nav>

      <div className="mt-auto rounded-xl border border-white/10 bg-gradient-to-br from-blue-600/14 to-cyan-500/10 p-4">
        {sidebarExpanded ? (
          <>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Quantum Hybrid</p>
            <p className="mt-2 text-sm font-medium text-white">Qiskit acceleration available</p>
            <p className="mt-1 text-xs leading-5 text-slate-400">Queue quantum-assisted tail calibration on selected simulations.</p>
          </>
        ) : (
          <div className="mx-auto size-8 rounded-lg bg-cyan-500/20" />
        )}
      </div>
    </aside>
  )
}
