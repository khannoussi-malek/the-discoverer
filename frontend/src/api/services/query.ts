/**
 * Query execution API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'
import type { QueryRequest, QueryResponse } from '@/types/query'

// Re-export types for convenience
export type { QueryRequest, QueryResponse } from '@/types/query'

export const queryService = {
  /**
   * Execute a natural language query
   */
  executeQuery: async (request: QueryRequest): Promise<QueryResponse> => {
    const params: Record<string, unknown> = {}
    if (request.page) params.page = request.page
    if (request.page_size) params.page_size = request.page_size

    const response = await apiClient.post(
      API_ENDPOINTS.QUERY.EXECUTE,
      {
        query: request.query,
        database_ids: request.database_ids,
      },
      { params }
    )
    return response.data
  },

  /**
   * Analyze a query without executing
   */
  analyzeQuery: async (query: string): Promise<unknown> => {
    const response = await apiClient.post(API_ENDPOINTS.QUERY.ANALYZE, { query })
    return response.data
  },

  /**
   * Get query history
   */
  getQueryHistory: async (limit?: number): Promise<unknown[]> => {
    const params = limit ? { limit } : {}
    const response = await apiClient.get(API_ENDPOINTS.QUERY.HISTORY, { params })
    return response.data
  },
}

