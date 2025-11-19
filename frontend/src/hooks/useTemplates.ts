/**
 * Custom hooks for template operations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { templatesService, type Template } from "@/api/services/templates"
import { queryKeys } from "@/lib/queryKeys"

export function useTemplates(params?: { page?: number; page_size?: number; tags?: string }) {
  return useQuery({
    queryKey: queryKeys.templates.list(params),
    queryFn: () => templatesService.listTemplates(params),
  })
}

export function useTemplate(id: string) {
  return useQuery({
    queryKey: queryKeys.templates.detail(id),
    queryFn: () => templatesService.getTemplate(id),
    enabled: !!id,
  })
}

export function useCreateTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (template: Omit<Template, 'id' | 'created_at' | 'updated_at'>) =>
      templatesService.createTemplate(template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.all })
    },
  })
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, template }: { id: string; template: Partial<Template> }) =>
      templatesService.updateTemplate(id, template),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.detail(variables.id) })
    },
  })
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => templatesService.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.templates.all })
    },
  })
}

export function useExecuteTemplate() {
  return useMutation({
    mutationFn: ({ id, parameters }: { id: string; parameters?: Record<string, unknown> }) =>
      templatesService.executeTemplate(id, parameters),
  })
}

