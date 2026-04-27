import { useAppStore } from '../../store/app-store'
import { Button } from '../ui/Button'
import type { AuthProfile } from '../../services/api'

export function Topbar({
  profile,
  onLogout,
  onExportReport,
}: {
  profile: AuthProfile | null
  onLogout: () => void
  onExportReport: () => void
}) {
  const setMobileDrawerOpen = useAppStore((state) => state.setMobileDrawerOpen)

  return (
    <div className="surface-panel mb-6 flex flex-col gap-4 px-5 py-4 xl:flex-row xl:items-center xl:justify-between">
      <div className="flex flex-1 items-center gap-3">
        <button
          type="button"
          onClick={() => setMobileDrawerOpen(true)}
          className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-white lg:hidden"
          aria-label="Open navigation"
        >
          <span className="space-y-1">
            <span className="block h-0.5 w-4 bg-current" />
            <span className="block h-0.5 w-4 bg-current" />
            <span className="block h-0.5 w-4 bg-current" />
          </span>
        </button>
        <div className="flex h-11 flex-1 items-center rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-slate-400">
          Search portfolios, reports, audit trails...
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">
          {profile?.tenant_name ?? 'Guest Workspace'}
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">3 alerts</div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">
          {profile ? `${profile.email} • ${profile.role}` : 'Guest session'}
        </div>
        <Button variant="secondary" className="h-11 px-4" onClick={onExportReport}>
          Export Report
        </Button>
        <Button variant="ghost" className="h-11 px-4" onClick={onLogout}>
          Log out
        </Button>
      </div>
    </div>
  )
}
