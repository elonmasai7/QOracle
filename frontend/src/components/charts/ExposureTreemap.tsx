import type { DashboardSnapshot } from '../../types/platform'

export function ExposureTreemap({ data }: { data: DashboardSnapshot['treemap'] }) {
  const total = data.reduce((sum, item) => sum + item.size, 0) || 1

  return (
    <div className="grid h-72 grid-cols-12 gap-3">
      {data.map((item) => (
        <div
          key={item.name}
          className="flex min-h-[88px] flex-col justify-between rounded-xl border border-white/10 p-4 text-white"
          style={{
            background: `linear-gradient(180deg, ${item.fill}, rgba(15, 27, 46, 0.88))`,
            gridColumn: `span ${Math.max(3, Math.round((item.size / total) * 12))}`,
          }}
        >
          <span className="text-sm font-semibold">{item.name}</span>
          <span className="text-xs text-slate-100/80">{item.size}% exposure</span>
        </div>
      ))}
      {data.length === 0 ? (
        <div className="col-span-12 flex items-center justify-center rounded-xl border border-white/10 bg-white/5 text-sm text-slate-400">
          No exposure data available.
        </div>
      ) : null}
    </div>
  )
}
