import { Button } from '../ui/Button'

export function Topbar() {
  return (
    <div className="surface-panel mb-6 flex flex-col gap-4 px-5 py-4 xl:flex-row xl:items-center xl:justify-between">
      <div className="flex flex-1 items-center gap-3">
        <div className="flex h-11 flex-1 items-center rounded-xl border border-white/10 bg-white/5 px-4 text-sm text-slate-400">
          Search portfolios, reports, audit trails...
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">Global Treasury Group</div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">3 alerts</div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-300">Amina Mensah</div>
        <Button variant="secondary" className="h-11 px-4">
          Export Report
        </Button>
      </div>
    </div>
  )
}
