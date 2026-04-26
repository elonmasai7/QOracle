import { useQueries } from '@tanstack/react-query'
import { mockSnapshot } from '../data/mockPlatform'
import { fetchDashboardSnapshot, fetchReportLibrary, fetchSecurityOverview, fetchStressScenarios } from '../services/api'
import type { DashboardSnapshot } from '../types/platform'

export function usePlatformSnapshot() {
  const [dashboardQuery, scenariosQuery, reportsQuery, securityQuery] = useQueries({
    queries: [
      {
        queryKey: ['dashboard-overview'],
        queryFn: fetchDashboardSnapshot,
        placeholderData: mockSnapshot,
      },
      {
        queryKey: ['risk-scenarios'],
        queryFn: fetchStressScenarios,
        staleTime: 5 * 60_000,
      },
      {
        queryKey: ['report-library'],
        queryFn: fetchReportLibrary,
        staleTime: 60_000,
      },
      {
        queryKey: ['security-overview'],
        queryFn: fetchSecurityOverview,
        staleTime: 60_000,
      },
    ],
  })

  const mergedSnapshot: DashboardSnapshot = {
    ...(dashboardQuery.data ?? mockSnapshot),
    reports: reportsQuery.data ?? dashboardQuery.data?.reports ?? mockSnapshot.reports,
    stressCards:
      scenariosQuery.data?.map((scenario) => ({
        name: scenario.name,
        shock: `${scenario.type.toUpperCase()} shock`,
        impact: formatScenarioImpact(scenario.parameters),
        severity: scenario.severity,
      })) ?? dashboardQuery.data?.stressCards ?? mockSnapshot.stressCards,
    auditLog: securityQuery.data?.auditLog ?? dashboardQuery.data?.auditLog ?? mockSnapshot.auditLog,
    apiKeys: securityQuery.data?.apiKeys ?? dashboardQuery.data?.apiKeys ?? mockSnapshot.apiKeys,
    securityControls: securityQuery.data?.controls ?? dashboardQuery.data?.securityControls ?? mockSnapshot.securityControls,
    rbacRoles: securityQuery.data?.rbac ?? dashboardQuery.data?.rbacRoles ?? mockSnapshot.rbacRoles,
  }

  return {
    data: mergedSnapshot,
    isLoading: dashboardQuery.isLoading,
    isFetching:
      dashboardQuery.isFetching ||
      scenariosQuery.isFetching ||
      reportsQuery.isFetching ||
      securityQuery.isFetching,
  }
}

function formatScenarioImpact(parameters: Record<string, number>) {
  const values = Object.values(parameters)
  if (values.length === 0) {
    return 'n/a'
  }
  const maxValue = Math.max(...values.map((value) => Math.abs(value)))
  return maxValue >= 100 ? `${Math.round(maxValue)} bps` : `${Math.round(maxValue)}%`
}
