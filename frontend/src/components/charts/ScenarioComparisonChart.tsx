import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { DashboardSnapshot } from '../../types/platform'

export function ScenarioComparisonChart({ data }: { data: DashboardSnapshot['scenarios'] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false} />
          <XAxis dataKey="name" stroke="#64748B" tickLine={false} axisLine={false} />
          <YAxis stroke="#64748B" tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 }} />
          <Legend />
          <Bar dataKey="base" fill="#2563EB" radius={[6, 6, 0, 0]} />
          <Bar dataKey="stressed" fill="#DC2626" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
