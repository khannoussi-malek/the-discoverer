/**
 * Custom hooks for dashboard operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { dashboardsService, type Dashboard } from "@/api/services/dashboards"
import { queryKeys } from "@/lib/queryKeys"

export function useDashboards(params?: { public_only?: boolean; tags?: string }) {
  return useQuery({
    queryKey: queryKeys.dashboards.list(params),
    queryFn: () => dashboardsService.listDashboards(params),
  })
}

export function useDashboard(id: string) {
  return useQuery({
    queryKey: queryKeys.dashboards.detail(id),
    queryFn: () => dashboardsService.getDashboard(id),
    enabled: !!id,
  })
}

export function useCreateDashboard() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (dashboard: Omit<Dashboard, 'id' | 'created_at' | 'updated_at'>) =>
      dashboardsService.createDashboard(dashboard),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboards.all })
    },
  })
}

export function useUpdateDashboard() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, dashboard }: { id: string; dashboard: Partial<Dashboard> }) =>
      dashboardsService.updateDashboard(id, dashboard),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboards.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboards.detail(variables.id) })
    },
  })
}

export function useDeleteDashboard() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => dashboardsService.deleteDashboard(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboards.all })
    },
  })
}

export function useRenderDashboard(id: string) {
  return useQuery({
    queryKey: queryKeys.dashboards.render(id),
    queryFn: () => dashboardsService.renderDashboard(id),
    enabled: !!id,
  })
}

