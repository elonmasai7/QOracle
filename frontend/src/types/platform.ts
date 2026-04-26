export type NavView =
  | 'dashboard'
  | 'portfolios'
  | 'risk-engine'
  | 'stress-testing'
  | 'forecasting'
  | 'reports'
  | 'compliance'
  | 'settings'

export interface MetricCard {
  id: string
  label: string
  value: string
  delta: string
  trend: 'up' | 'down' | 'neutral'
  metadata: string
  sparkline: number[]
}

export interface RecommendationCard {
  title: string
  confidence: number
  impact: number
  rationale: string
  action: string
}

export interface ScenarioCard {
  name: string
  shock: string
  impact: string
  severity: 'low' | 'medium' | 'high'
}

export interface PortfolioHolding {
  desk: string
  allocation: number
  varContribution: number
}

export interface HeatmapCell {
  x: string
  y: string
  value: number
}

export interface TreemapNode {
  name: string
  size: number
  fill: string
}

export interface DashboardSnapshot {
  metrics: MetricCard[]
  riskTrend: { label: string; risk: number; var95: number }[]
  histogram: { bucket: string; frequency: number }[]
  tailRisk: { percentile: string; loss: number; marker?: 'VaR' | 'CVaR' }[]
  heatmap: HeatmapCell[]
  treemap: TreemapNode[]
  scenarios: { name: string; base: number; stressed: number }[]
  recommendations: RecommendationCard[]
  stressCards: ScenarioCard[]
  workflowSteps: { title: string; status: 'complete' | 'active' | 'pending'; detail: string }[]
  reports: { title: string; updatedAt: string; format: string; owner: string }[]
  auditLog: { event: string; actor: string; timestamp: string; channel: string }[]
  apiKeys: { name: string; scope: string; lastUsed: string; status: string }[]
  exposures: PortfolioHolding[]
  securityControls?: string[]
  rbacRoles?: { role: string; capabilities: string[] }[]
}

export interface SecurityOverview {
  rbac: { role: string; capabilities: string[] }[]
  auditLog: DashboardSnapshot['auditLog']
  apiKeys: DashboardSnapshot['apiKeys']
  controls: string[]
}

export interface StressScenarioResponse {
  name: string
  type: string
  severity: 'low' | 'medium' | 'high'
  parameters: Record<string, number>
}
