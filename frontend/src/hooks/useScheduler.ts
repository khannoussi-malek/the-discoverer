/**
 * Custom hooks for scheduler operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { schedulerService, type ScheduledQuery } from "@/api/services/scheduler"
import { queryKeys } from "@/lib/queryKeys"

export function useSchedules() {
  return useQuery({
    queryKey: queryKeys.schedules.list(),
    queryFn: () => schedulerService.listSchedules(),
  })
}

export function useSchedule(id: string) {
  return useQuery({
    queryKey: queryKeys.schedules.detail(id),
    queryFn: () => schedulerService.getSchedule(id),
    enabled: !!id,
  })
}

export function useCreateSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (schedule: Omit<ScheduledQuery, 'id' | 'created_at' | 'updated_at' | 'last_run' | 'next_run'>) =>
      schedulerService.createSchedule(schedule),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all })
    },
  })
}

export function useUpdateSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, schedule }: { id: string; schedule: Partial<ScheduledQuery> }) =>
      schedulerService.updateSchedule(id, schedule),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.detail(variables.id) })
    },
  })
}

export function useDeleteSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => schedulerService.deleteSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all })
    },
  })
}

export function useEnableSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => schedulerService.enableSchedule(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.detail(id) })
    },
  })
}

export function useDisableSchedule() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => schedulerService.disableSchedule(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.schedules.detail(id) })
    },
  })
}

