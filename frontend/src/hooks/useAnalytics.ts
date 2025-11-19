/**
 * Custom hooks for analytics
 */

import { useQuery } from "@tanstack/react-query"
import { analyticsService } from "@/api/services/analytics"
import { queryKeys } from "@/lib/queryKeys"

export function useAnalyticsStats(days: number = 7) {
  return useQuery({
    queryKey: queryKeys.analytics.stats(days),
    queryFn: () => analyticsService.getStats(days),
  })
}

export function useTopQueries(limit: number = 10, days: number = 7) {
  return useQuery({
    queryKey: queryKeys.analytics.topQueries(limit, days),
    queryFn: () => analyticsService.getTopQueries(limit, days),
  })
}

