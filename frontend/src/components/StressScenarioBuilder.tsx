import React, { useState } from 'react'

export const StressScenarioBuilder: React.FC = () => {
  const [fedShock, setFedShock] = useState(2)
  const [cpiSpike, setCpiSpike] = useState(3)
  const [gdpDrop, setGdpDrop] = useState(2)

  return (
    <div className="panel">
      <h4>Stress Scenario Builder (U.S.)</h4>
      <label>Fed Funds Shock (%)</label>
      <input type="range" min="0" max="10" value={fedShock} onChange={(e) => setFedShock(Number(e.target.value))} />
      <label>CPI Spike (%)</label>
      <input type="range" min="0" max="12" value={cpiSpike} onChange={(e) => setCpiSpike(Number(e.target.value))} />
      <label>GDP Contraction (%)</label>
      <input type="range" min="0" max="8" value={gdpDrop} onChange={(e) => setGdpDrop(Number(e.target.value))} />
      <p className="muted">Scenario: +{fedShock}% Fed, +{cpiSpike}% CPI, -{gdpDrop}% GDP</p>
    </div>
  )
}
