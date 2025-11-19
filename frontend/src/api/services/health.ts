/**
 * Health check API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  services?: Record<string, string>
}

export const healthService = {
  /**
   * Check API health
   */
  checkHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH)
    return response.data
  },
}

