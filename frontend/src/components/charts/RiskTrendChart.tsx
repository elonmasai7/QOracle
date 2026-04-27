import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { DashboardSnapshot } from '../../types/platform'

export function RiskTrendChart({ data }: { data: DashboardSnapshot['riskTrend'] }) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="riskFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,.08)" vertical={false} />
          <XAxis dataKey="label" stroke="#64748B" tickLine={false} axisLine={false} />
          <YAxis stroke="#64748B" tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{ background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 }}
            labelStyle={{ color: '#F8FAFC' }}
          />
          <Area type="monotone" dataKey="risk" stroke="#2563EB" strokeWidth={2} fill="url(#riskFill)" isAnimationActive={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
