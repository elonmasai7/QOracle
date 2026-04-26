import { useQuery } from '@tanstack/react-query'
import { mockSnapshot } from '../data/mockPlatform'
import { fetchDashboardSnapshot } from '../services/api'

export function usePlatformSnapshot() {
  return useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: fetchDashboardSnapshot,
    placeholderData: mockSnapshot,
  })
}
