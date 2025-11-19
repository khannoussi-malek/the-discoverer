/**
 * Query result sharing API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface ShareOptions {
  query_id: string
  expires_in_hours?: number
  max_accesses?: number
  allowed_emails?: string[]
  password?: string
}

export interface ShareResponse {
  share_id: string
  share_token: string
  share_url: string
  expires_at: string | null
  max_accesses: number | null
  created_at: string
}

export const sharingService = {
  /**
   * Create a shareable link for query result
   */
  createShare: async (options: ShareOptions): Promise<ShareResponse> => {
    const response = await apiClient.post(API_ENDPOINTS.SHARING.CREATE, options)
    return response.data
  },

  /**
   * Get shared result by token
   */
  getSharedResult: async (token: string, password?: string): Promise<unknown> => {
    const params = password ? { password } : {}
    const response = await apiClient.get(API_ENDPOINTS.SHARING.GET(token), { params })
    return response.data
  },

  /**
   * List all shares
   */
  listShares: async (queryId?: string): Promise<ShareResponse[]> => {
    const params = queryId ? { query_id: queryId } : {}
    const response = await apiClient.get(API_ENDPOINTS.SHARING.LIST, { params })
    return response.data
  },

  /**
   * Revoke a share
   */
  revokeShare: async (id: string): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.SHARING.REVOKE(id))
  },

  /**
   * Delete a share
   */
  deleteShare: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.SHARING.DELETE(id))
  },
}

