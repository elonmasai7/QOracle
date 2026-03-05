import React from 'react'
import { KpiCard } from '../components/KpiCard'
import { RiskChart } from '../components/RiskChart'
import { StressScenarioBuilder } from '../components/StressScenarioBuilder'

export const App: React.FC = () => {
  return (
    <div className="app-shell">
      <header>
        <h1>QuantumRisk Oracle</h1>
        <p>Hybrid Quantum + ML Financial Risk Intelligence</p>
      </header>

      <section className="kpi-grid">
        <KpiCard label="VaR (99%)" value="$1.28M" />
        <KpiCard label="CVaR" value="$1.61M" />
        <KpiCard label="Expected Shortfall" value="$1.57M" />
        <KpiCard label="Composite Risk Score" value="51 / 100" />
      </section>

      <section className="grid-2">
        <RiskChart />
        <StressScenarioBuilder />
      </section>

      <section className="panel">
        <h4>Compliance Exports</h4>
        <div className="button-row">
          <button>Export PDF</button>
          <button>Export CSV</button>
          <button>Export JSON</button>
        </div>
      </section>
    </div>
  )
}
