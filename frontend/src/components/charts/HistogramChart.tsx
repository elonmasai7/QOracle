import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { DashboardSnapshot } from '../../types/platform'

export function HistogramChart({ data }: { data: DashboardSnapshot['histogram'] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false} />
          <XAxis dataKey="bucket" stroke="#64748B" tickLine={false} axisLine={false} />
          <YAxis stroke="#64748B" tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 }} />
          <Bar dataKey="frequency" fill="#0891B2" radius={[6, 6, 0, 0]} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
