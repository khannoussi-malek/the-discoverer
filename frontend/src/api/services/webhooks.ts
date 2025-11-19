/**
 * Webhooks API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface Webhook {
  id: string
  url: string
  events: string[]
  secret?: string
  enabled: boolean
  created_at?: string
  updated_at?: string
}

export const webhooksService = {
  /**
   * List all webhooks
   */
  listWebhooks: async (): Promise<Webhook[]> => {
    const response = await apiClient.get(API_ENDPOINTS.WEBHOOKS.LIST)
    return response.data
  },

  /**
   * Get webhook by ID
   */
  getWebhook: async (id: string): Promise<Webhook> => {
    const response = await apiClient.get(API_ENDPOINTS.WEBHOOKS.GET(id))
    return response.data
  },

  /**
   * Create a new webhook
   */
  createWebhook: async (webhook: Omit<Webhook, 'id' | 'created_at' | 'updated_at'>): Promise<Webhook> => {
    const response = await apiClient.post(API_ENDPOINTS.WEBHOOKS.CREATE, webhook)
    return response.data
  },

  /**
   * Update webhook
   */
  updateWebhook: async (id: string, webhook: Partial<Webhook>): Promise<Webhook> => {
    const response = await apiClient.put(API_ENDPOINTS.WEBHOOKS.UPDATE(id), webhook)
    return response.data
  },

  /**
   * Delete webhook
   */
  deleteWebhook: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.WEBHOOKS.DELETE(id))
  },
}

