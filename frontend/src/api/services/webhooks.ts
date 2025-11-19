/**
 * Webhooks API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'
import type { Webhook, WebhookStats, WebhookCreateRequest, WebhookUpdateRequest } from '@/types/webhooks'

// Re-export types for convenience
export type { Webhook, WebhookStats, WebhookCreateRequest, WebhookUpdateRequest } from '@/types/webhooks'

interface WebhooksListResponse {
  webhooks: Webhook[]
  total: number
}

export const webhooksService = {
  /**
   * List all webhooks
   */
  listWebhooks: async (params?: { event?: string; active_only?: boolean }): Promise<Webhook[]> => {
    const response = await apiClient.get<WebhooksListResponse>(API_ENDPOINTS.WEBHOOKS.LIST, { params })
    // Backend returns {webhooks: [...], total: ...}, extract webhooks array
    return response.data.webhooks || []
  },

  /**
   * Get webhook by ID
   */
  getWebhook: async (id: string): Promise<Webhook> => {
    const response = await apiClient.get<Webhook>(API_ENDPOINTS.WEBHOOKS.GET(id))
    return response.data
  },

  /**
   * Create a new webhook
   */
  createWebhook: async (webhook: WebhookCreateRequest): Promise<Webhook> => {
    const response = await apiClient.post<Webhook>(API_ENDPOINTS.WEBHOOKS.CREATE, webhook)
    return response.data
  },

  /**
   * Update webhook
   */
  updateWebhook: async (id: string, webhook: WebhookUpdateRequest): Promise<Webhook> => {
    const response = await apiClient.put<Webhook>(API_ENDPOINTS.WEBHOOKS.UPDATE(id), webhook)
    return response.data
  },

  /**
   * Delete webhook
   */
  deleteWebhook: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.WEBHOOKS.DELETE(id))
  },

  /**
   * Get webhook statistics
   */
  getWebhookStats: async (id: string): Promise<WebhookStats> => {
    const response = await apiClient.get<WebhookStats>(API_ENDPOINTS.WEBHOOKS.STATS(id))
    return response.data
  },

  /**
   * Test webhook
   */
  testWebhook: async (id: string, payload?: Record<string, unknown>): Promise<unknown> => {
    const response = await apiClient.post(API_ENDPOINTS.WEBHOOKS.TEST(id), payload)
    return response.data
  },
}

