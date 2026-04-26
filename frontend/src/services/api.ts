import axios from 'axios'
import type { DashboardSnapshot } from '../types/platform'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchDashboardSnapshot(): Promise<DashboardSnapshot> {
  const response = await api.get<DashboardSnapshot>('/api/v1/dashboard/overview')
  return response.data
}
