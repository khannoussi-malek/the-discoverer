/**
 * Webhook types and interfaces
 */

export type WebhookEvent =
  | 'query.completed'
  | 'query.failed'
  | 'database.registered'
  | 'database.synced'
  | 'schema.changed'
  | 'dashboard.created'
  | 'dashboard.updated'
  | 'export.completed'

export interface Webhook {
  id: string
  url: string
  events: WebhookEvent[]
  secret?: string // Only returned on creation
  active: boolean
  headers?: Record<string, string>
  timeout?: number
  success_count?: number
  failure_count?: number
  last_triggered?: string
  created_at?: string
  updated_at?: string
}

export interface WebhookStats {
  webhook_id: string
  success_count: number
  failure_count: number
  total_attempts: number
  success_rate: number
  last_triggered?: string
  last_success?: string
  last_failure?: string
}

export interface WebhookCreateRequest {
  url: string
  events: WebhookEvent[]
  headers?: Record<string, string>
  timeout?: number
}

export interface WebhookUpdateRequest {
  url?: string
  events?: WebhookEvent[]
  active?: boolean
  headers?: Record<string, string>
  timeout?: number
}

