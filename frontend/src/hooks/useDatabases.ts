/**
 * Custom hooks for database operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { discoveryService } from "@/api/services/discovery"
import type { DatabaseConfig } from "@/types/database"
import { queryKeys } from "@/lib/queryKeys"

export function useDatabases() {
  return useQuery({
    queryKey: queryKeys.databases.list(),
    queryFn: () => discoveryService.listDatabases(),
  })
}

export function useDatabase(id: string) {
  return useQuery({
    queryKey: queryKeys.databases.detail(id),
    queryFn: () => discoveryService.getDatabase(id),
    enabled: !!id,
  })
}

export function useRegisterDatabase() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (config: DatabaseConfig) => discoveryService.registerDatabase(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.databases.all })
    },
  })
}

export function useSyncDatabase() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => discoveryService.syncDatabase(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.databases.all })
    },
  })
}

