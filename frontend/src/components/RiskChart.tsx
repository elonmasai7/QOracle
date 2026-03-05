import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { day: 'Mon', risk: 42 },
  { day: 'Tue', risk: 47 },
  { day: 'Wed', risk: 44 },
  { day: 'Thu', risk: 51 },
  { day: 'Fri', risk: 49 }
]

export const RiskChart: React.FC = () => (
  <div className="panel">
    <h4>Risk Trend Analytics</h4>
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data}>
        <XAxis dataKey="day" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="risk" stroke="#146b5b" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  </div>
)
