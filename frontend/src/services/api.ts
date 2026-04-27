import axios from 'axios'
import type { AxiosError } from 'axios'
import type { DashboardSnapshot, SecurityOverview, StressScenarioResponse } from '../types/platform'

export interface LoginResponse {
  access_token: string
  tenant_id: string
  role: string
}

export interface RegisterResponse {
  tenant_id: string
  organization_id: string
  user_id: string
}

export interface AuthProfile {
  user_id: string
  tenant_id: string
  email: string
  role: string
  tenant_name: string | null
  plan: string | null
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export function setAccessToken(accessToken: string | null) {
  if (accessToken) {
    api.defaults.headers.common.Authorization = `Bearer ${accessToken}`
    return
  }
  delete api.defaults.headers.common.Authorization
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/api/v1/auth/login', { email, password })
  return response.data
}

export async function registerAccount(input: {
  organization_name: string
  email: string
  password: string
  role?: string
}): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>('/api/v1/auth/register', input)
  return response.data
}

export async function fetchCurrentUser(): Promise<AuthProfile> {
  const response = await api.get<AuthProfile>('/api/v1/auth/me')
  return response.data
}

export function describeApiError(error: unknown): string {
  const axiosError = error as AxiosError<{ error?: string }>
  const status = axiosError.response?.status
  const code = axiosError.response?.data?.error

  if (status === 401 || code === 'invalid_credentials') {
    return 'Unable to sign in with those credentials. Use one of the seeded demo accounts and try again.'
  }

  if (status === 409 || code === 'email_already_registered') {
    return 'That email is already registered. Try signing in instead.'
  }

  if (status === 400 && code === 'password_too_short') {
    return 'Password must be at least 8 characters long.'
  }

  if (!axiosError.response) {
    return 'The backend is unreachable. Start the backend on http://localhost:8000 and try again.'
  }

  return 'Sign-in failed because the server returned an unexpected response. Please try again.'
}

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
