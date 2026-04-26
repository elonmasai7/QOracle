import { Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from 'recharts'
import type { DashboardSnapshot } from '../../types/platform'

export function TailRiskChart({ data }: { data: DashboardSnapshot['tailRisk'] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="percentile" stroke="#64748B" tickLine={false} axisLine={false} />
          <YAxis stroke="#64748B" tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 }} />
          <Bar dataKey="loss" radius={[6, 6, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.percentile}
                fill={entry.marker === 'CVaR' ? '#DC2626' : entry.marker === 'VaR' ? '#D97706' : '#2563EB'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
