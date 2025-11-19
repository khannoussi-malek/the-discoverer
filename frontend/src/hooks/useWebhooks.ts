/**
 * Custom hooks for webhook operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { webhooksService, type WebhookCreateRequest, type WebhookUpdateRequest } from "@/api/services/webhooks"
import { queryKeys } from "@/lib/queryKeys"

export function useWebhooks(params?: { event?: string; active_only?: boolean }) {
  return useQuery({
    queryKey: queryKeys.webhooks.list(),
    queryFn: () => webhooksService.listWebhooks(params),
  })
}

export function useWebhook(id: string) {
  return useQuery({
    queryKey: queryKeys.webhooks.detail(id),
    queryFn: () => webhooksService.getWebhook(id),
    enabled: !!id,
  })
}

export function useCreateWebhook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (webhook: WebhookCreateRequest) => webhooksService.createWebhook(webhook),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks.all })
    },
  })
}

export function useUpdateWebhook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, webhook }: { id: string; webhook: WebhookUpdateRequest }) =>
      webhooksService.updateWebhook(id, webhook),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks.detail(variables.id) })
    },
  })
}

export function useDeleteWebhook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => webhooksService.deleteWebhook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks.all })
    },
  })
}

export function useWebhookStats(id: string) {
  return useQuery({
    queryKey: [...queryKeys.webhooks.detail(id), 'stats'],
    queryFn: () => webhooksService.getWebhookStats(id),
    enabled: !!id,
  })
}

export function useTestWebhook() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload?: Record<string, unknown> }) =>
      webhooksService.testWebhook(id, payload),
    onSuccess: (_, variables) => {
      // Invalidate stats after testing
      queryClient.invalidateQueries({ queryKey: [...queryKeys.webhooks.detail(variables.id), 'stats'] })
      queryClient.invalidateQueries({ queryKey: queryKeys.webhooks.detail(variables.id) })
    },
  })
}

