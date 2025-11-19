/**
 * Templates API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface Template {
  id: string
  name: string
  user_query: string
  database_ids?: string[]
  description?: string
  tags?: string[]
  created_at?: string
  updated_at?: string
}

export const templatesService = {
  /**
   * List all templates
   */
  listTemplates: async (params?: { page?: number; page_size?: number; tags?: string }): Promise<{ templates: Template[]; total: number }> => {
    const response = await apiClient.get(API_ENDPOINTS.TEMPLATES.LIST, { params })
    return response.data
  },

  /**
   * Get template by ID
   */
  getTemplate: async (id: string): Promise<Template> => {
    const response = await apiClient.get(API_ENDPOINTS.TEMPLATES.GET(id))
    return response.data
  },

  /**
   * Create a new template
   */
  createTemplate: async (template: Omit<Template, 'id' | 'created_at' | 'updated_at'>): Promise<Template> => {
    const response = await apiClient.post(API_ENDPOINTS.TEMPLATES.CREATE, template)
    return response.data
  },

  /**
   * Update template
   */
  updateTemplate: async (id: string, template: Partial<Template>): Promise<Template> => {
    const response = await apiClient.put(API_ENDPOINTS.TEMPLATES.UPDATE(id), template)
    return response.data
  },

  /**
   * Delete template
   */
  deleteTemplate: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.TEMPLATES.DELETE(id))
  },

  /**
   * Execute template with parameters
   */
  executeTemplate: async (id: string, parameters?: Record<string, unknown>): Promise<unknown> => {
    const response = await apiClient.post(API_ENDPOINTS.TEMPLATES.EXECUTE(id), { parameters })
    return response.data
  },
}

