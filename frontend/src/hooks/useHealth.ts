/**
 * Custom hooks for health check
 */

import { useQuery } from "@tanstack/react-query"
import { healthService } from "@/api/services/health"
import { queryKeys } from "@/lib/queryKeys"

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health.check(),
    queryFn: () => healthService.checkHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

