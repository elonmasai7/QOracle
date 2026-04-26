import { ResponsiveContainer, Tooltip, Treemap } from 'recharts'
import type { DashboardSnapshot } from '../../types/platform'

export function ExposureTreemap({ data }: { data: DashboardSnapshot['treemap'] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <Treemap data={data} dataKey="size" stroke="rgba(255,255,255,.16)" fill="#2563EB">
          <Tooltip contentStyle={{ background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 }} />
        </Treemap>
      </ResponsiveContainer>
    </div>
  )
}
