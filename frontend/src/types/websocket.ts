/**
 * WebSocket message types and interfaces
 */

export type WebSocketMessageType = 'connected' | 'query_update' | 'pong' | 'error'

export interface BaseWebSocketMessage {
  type: WebSocketMessageType
  timestamp?: number
}

export interface ConnectedMessage extends BaseWebSocketMessage {
  type: 'connected'
  query_id?: string
  message: string
}

export interface QueryUpdateMessage extends BaseWebSocketMessage {
  type: 'query_update'
  query_id: string
  data: {
    status?: string
    total_rows?: number
    page?: number
    page_size?: number
    [key: string]: unknown
  }
}

export interface PongMessage extends BaseWebSocketMessage {
  type: 'pong'
  timestamp: number
}

export interface ErrorMessage extends BaseWebSocketMessage {
  type: 'error'
  message: string
}

export type WebSocketMessage =
  | ConnectedMessage
  | QueryUpdateMessage
  | PongMessage
  | ErrorMessage

