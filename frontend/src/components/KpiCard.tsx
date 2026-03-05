import React from 'react'

type Props = {
  label: string
  value: string
}

export const KpiCard: React.FC<Props> = ({ label, value }) => (
  <div className="kpi-card">
    <p>{label}</p>
    <h3>{value}</h3>
  </div>
)
