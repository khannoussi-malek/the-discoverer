/**
 * Export API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export type ExportFormat = 'csv' | 'json' | 'excel' | 'parquet' | 'avro'

export const exportService = {
  /**
   * Export query results
   */
  exportQuery: async (queryId: string, format: ExportFormat = 'csv'): Promise<Blob> => {
    const response = await apiClient.get(API_ENDPOINTS.EXPORT.QUERY(queryId), {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },
}

