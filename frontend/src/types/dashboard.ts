/**
 * Dashboard types
 */

export interface DashboardWidget {
  type: 'chart' | 'metric' | 'query' | 'text'
  title: string
  query_id?: string
  chart_template_id?: string
  position: { x: number; y: number; width: number; height: number }
  config?: Record<string, unknown>
}

export interface Dashboard {
  id: string
  name: string
  description?: string
  widgets: DashboardWidget[]
  layout?: Record<string, unknown>
  tags?: string[]
  is_public: boolean
  created_at?: string
  updated_at?: string
}

export interface DashboardLayout {
  grid: string // e.g., "12x8"
  columns?: number
  rows?: number
}

