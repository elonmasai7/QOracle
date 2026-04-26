import { Fragment } from 'react'
import { scaleLinear } from 'd3-scale'
import type { DashboardSnapshot } from '../../types/platform'

export function CorrelationHeatmap({ data }: { data: DashboardSnapshot['heatmap'] }) {
  const labels = [...new Set(data.map((cell) => cell.x))]
  const color = scaleLinear<string>().domain([0, 0.5, 1]).range(['#0F1B2E', '#2563EB', '#8B5CF6'])

  return (
    <div className="overflow-x-auto">
      <div className="grid min-w-[420px] grid-cols-[100px_repeat(4,1fr)] gap-2">
        <div />
        {labels.map((label) => (
          <div key={label} className="px-2 text-xs font-medium text-slate-400">
            {label}
          </div>
        ))}
        {labels.map((row) => (
          <Fragment key={row}>
            <div key={`${row}-label`} className="flex items-center px-2 text-xs font-medium text-slate-400">
              {row}
            </div>
            {labels.map((column) => {
              const cell = data.find((item) => item.x === row && item.y === column)
              const value = cell?.value ?? 0
              return (
                <div
                  key={`${row}-${column}`}
                  className="flex aspect-square items-center justify-center rounded-xl border border-white/5 text-xs font-semibold text-white"
                  style={{ backgroundColor: color(value) }}
                >
                  {value.toFixed(2)}
                </div>
              )
            })}
          </Fragment>
        ))}
      </div>
    </div>
  )
}
