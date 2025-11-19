/**
 * Common type definitions for JSON data
 */

export type JsonValue = 
  | string 
  | number 
  | boolean 
  | null 
  | JsonObject 
  | JsonArray

export interface JsonObject {
  [key: string]: JsonValue
}

export type JsonArray = JsonValue[]

export type ApiResponse<T = unknown> = {
  data: T
  message?: string
  status?: number
}

export type PaginatedResponse<T = unknown> = {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

