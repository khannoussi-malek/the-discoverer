/**
 * Dashboards API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

import type { Dashboard, DashboardWidget } from '@/types/dashboard'

// Re-export types for convenience
export type { Dashboard } from '@/types/dashboard'

interface BackendDashboardItem {
  id: string
  name: string
  description?: string
  widget_count?: number
  created_at?: string
  updated_at?: string
  is_public: boolean
  tags?: string[]
  widgets?: DashboardWidget[] // May be present in some responses
}

interface DashboardsListResponse {
  dashboards: BackendDashboardItem[]
  total: number
}

export const dashboardsService = {
  /**
   * List all dashboards
   */
  listDashboards: async (params?: { public_only?: boolean; tags?: string }): Promise<Dashboard[]> => {
    const response = await apiClient.get<DashboardsListResponse>(API_ENDPOINTS.DASHBOARDS.LIST, { params })
    // Backend returns {dashboards: [...], total: ...}, extract dashboards array
    const dashboards = response.data.dashboards || []
    // Map backend response to frontend Dashboard type
    // Backend returns widget_count but frontend expects widgets array
    return dashboards.map((d: BackendDashboardItem): Dashboard => ({
      id: d.id,
      name: d.name,
      description: d.description,
      widgets: d.widgets || [], // Use widgets if present, otherwise empty array
      layout: undefined, // Not returned in list endpoint
      tags: d.tags,
      is_public: d.is_public,
      created_at: d.created_at,
      updated_at: d.updated_at,
    }))
  },

  /**
   * Get dashboard by ID
   */
  getDashboard: async (id: string): Promise<Dashboard> => {
    const response = await apiClient.get(API_ENDPOINTS.DASHBOARDS.GET(id))
    return response.data
  },

  /**
   * Create a new dashboard
   */
  createDashboard: async (dashboard: Omit<Dashboard, 'id' | 'created_at' | 'updated_at'>): Promise<Dashboard> => {
    const response = await apiClient.post(API_ENDPOINTS.DASHBOARDS.CREATE, dashboard)
    return response.data
  },

  /**
   * Update dashboard
   */
  updateDashboard: async (id: string, dashboard: Partial<Dashboard>): Promise<Dashboard> => {
    const response = await apiClient.put(API_ENDPOINTS.DASHBOARDS.UPDATE(id), dashboard)
    return response.data
  },

  /**
   * Delete dashboard
   */
  deleteDashboard: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.DASHBOARDS.DELETE(id))
  },

  /**
   * Render dashboard with populated data
   */
  renderDashboard: async (id: string): Promise<Dashboard> => {
    const response = await apiClient.get(API_ENDPOINTS.DASHBOARDS.RENDER(id))
    return response.data
  },
}

