/**
 * Custom hooks for query operations
 */

import { useMutation, useQuery } from "@tanstack/react-query"
import { queryService, type QueryRequest } from "@/api/services/query"
import { queryKeys } from "@/lib/queryKeys"

export function useExecuteQuery() {
  return useMutation({
    mutationFn: (request: QueryRequest) => queryService.executeQuery(request),
  })
}

export function useQueryHistory(limit?: number) {
  return useQuery({
    queryKey: queryKeys.queries.history(limit),
    queryFn: () => queryService.getQueryHistory(limit),
  })
}

export function useAnalyzeQuery() {
  return useMutation({
    mutationFn: (query: string) => queryService.analyzeQuery(query),
  })
}

