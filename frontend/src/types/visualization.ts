/**
 * Visualization types
 */

export type ChartType = 
  | 'bar' 
  | 'line' 
  | 'pie' 
  | 'area' 
  | 'scatter' 
  | 'heatmap' 
  | 'box' 
  | 'violin' 
  | '3d' 
  | 'surface' 
  | 'sunburst' 
  | 'treemap' 
  | 'funnel' 
  | 'gauge' 
  | 'waterfall'

export interface ChartConfig {
  query_id: string
  chart_type?: ChartType
  x_axis?: string
  y_axis?: string
  z_axis?: string
  title?: string
  config?: Record<string, unknown>
}

export interface ChartResponse {
  chart_type: string
  data: Record<string, unknown>[]
  config: Record<string, unknown>
}

export type ChartExportFormat = 'png' | 'pdf' | 'html' | 'svg'

