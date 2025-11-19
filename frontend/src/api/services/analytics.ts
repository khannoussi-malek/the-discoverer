/**
 * Analytics API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface AnalyticsStats {
  total_queries: number
  avg_execution_time: number
  total_databases: number
  cache_hit_rate?: number
}

export interface TopQuery {
  query: string
  count: number
  avg_execution_time: number
}

export const analyticsService = {
  /**
   * Get analytics statistics
   */
  getStats: async (days: number = 7): Promise<AnalyticsStats> => {
    const response = await apiClient.get(API_ENDPOINTS.ANALYTICS.STATS, {
      params: { days },
    })
    return response.data
  },

  /**
   * Get top queries
   */
  getTopQueries: async (limit: number = 10, days: number = 7): Promise<TopQuery[]> => {
    const response = await apiClient.get(API_ENDPOINTS.ANALYTICS.TOP_QUERIES, {
      params: { limit, days },
    })
    return response.data
  },
}

