/**
 * Query types
 */

export interface QueryRequest {
  query: string
  database_ids?: string[]
  page?: number
  page_size?: number
}

export interface QueryResponse {
  query_id: string
  data?: Record<string, unknown>[]
  results?: Record<string, unknown>[]
  total_rows: number
  execution_time: number
  databases_queried: string[]
  page?: number
  page_size?: number
  total_pages?: number
  cached?: boolean
}

export interface QueryHistory {
  query_id: string
  query: string
  execution_time: number
  total_rows: number
  executed_at: string
  databases_queried: string[]
}

