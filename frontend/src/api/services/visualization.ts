/**
 * Visualization API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

import type { ChartResponse } from '@/types/visualization'

export interface VisualizationRequest {
  query_id: string
  chart_type?: string
  x_axis?: string
  y_axis?: string
  z_axis?: string
  title?: string
  config?: Record<string, unknown>
}

export const visualizationService = {
  /**
   * Generate a chart from query results
   */
  generateChart: async (request: VisualizationRequest): Promise<ChartResponse> => {
    const response = await apiClient.post(API_ENDPOINTS.VISUALIZATION.GENERATE, request)
    return response.data
  },

  /**
   * Export chart as image/PDF
   */
  exportChart: async (
    queryId: string,
    format: 'png' | 'pdf' | 'html' | 'svg' = 'png',
    width?: number,
    height?: number
  ): Promise<Blob> => {
    const params: Record<string, unknown> = { format }
    if (width) params.width = width
    if (height) params.height = height

    const response = await apiClient.get(API_ENDPOINTS.VISUALIZATION.EXPORT(queryId), {
      params,
      responseType: 'blob',
    })
    return response.data
  },
}

