import axios from 'axios'
import type { DashboardSnapshot, SecurityOverview, StressScenarioResponse } from '../types/platform'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchDashboardSnapshot(): Promise<DashboardSnapshot> {
  const response = await api.get<DashboardSnapshot>('/api/v1/dashboard/overview')
  return response.data
}

export async function fetchStressScenarios(): Promise<StressScenarioResponse[]> {
  const response = await api.get<StressScenarioResponse[]>('/api/v1/risk/scenarios')
  return response.data
}

export async function fetchReportLibrary(): Promise<DashboardSnapshot['reports']> {
  const response = await api.get<DashboardSnapshot['reports']>('/api/v1/reports/library')
  return response.data
}

export async function fetchSecurityOverview(): Promise<SecurityOverview> {
  const response = await api.get<SecurityOverview>('/api/v1/security/overview')
  return response.data
}
