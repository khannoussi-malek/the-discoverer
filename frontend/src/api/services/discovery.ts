/**
 * Database discovery API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'
import type { Database, DatabaseConfig } from '@/types/database'

export const discoveryService = {
  /**
   * Register a new database
   */
  registerDatabase: async (config: DatabaseConfig): Promise<Database> => {
    const response = await apiClient.post(API_ENDPOINTS.DISCOVERY.DATABASES, config)
    return response.data
  },

  /**
   * List all databases
   */
  listDatabases: async (): Promise<Database[]> => {
    const response = await apiClient.get(API_ENDPOINTS.DISCOVERY.DATABASES)
    return response.data
  },

  /**
   * Get database by ID
   */
  getDatabase: async (id: string): Promise<Database> => {
    const response = await apiClient.get(API_ENDPOINTS.DISCOVERY.DATABASE(id))
    return response.data
  },

  /**
   * Sync database schema
   */
  syncDatabase: async (id: string): Promise<Database> => {
    const response = await apiClient.post(API_ENDPOINTS.DISCOVERY.SYNC(id))
    return response.data
  },
}

