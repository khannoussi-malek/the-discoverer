/**
 * Database types
 */

export interface Database {
  id: string
  type: string
  name: string
  host: string
  port: number
  database_name: string
  is_active: boolean
  last_synced?: string
}

export interface DatabaseConfig {
  id: string
  type: string
  name?: string
  host: string
  port: number
  database: string
  user?: string
  password?: string
  metadata?: Record<string, unknown>
}

export type DatabaseType = 'postgresql' | 'mysql' | 'sqlite' | 'mssql' | 'oracle'

