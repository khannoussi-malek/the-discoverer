/**
 * Custom hook for query-specific WebSocket connections
 * Uses react-use-websocket library for WebSocket management
 */

import { useEffect, useRef, useMemo } from 'react'
import useWebSocket from 'react-use-websocket'
import { getWebSocketUrl } from '@/config/env'
import { API_ENDPOINTS } from '@/api/endpoints'
import type { WebSocketMessage } from '@/types/websocket'

interface UseQueryWebSocketOptions {
  queryId: string | null
  enabled?: boolean
  onMessage?: (message: WebSocketMessage) => void
}

interface UseQueryWebSocketReturn {
  lastMessage: WebSocketMessage | null
  sendMessage: (message: object) => void
  readyState: number
  isConnected: boolean
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error'
}

/**
 * Hook for subscribing to query-specific WebSocket updates
 * @param options - Configuration options
 * @returns WebSocket connection state and methods
 */
export function useQueryWebSocket({
  queryId,
  enabled = true,
  onMessage,
}: UseQueryWebSocketOptions): UseQueryWebSocketReturn {
  const pingIntervalRef = useRef<number | null>(null)
  const onMessageRef = useRef(onMessage)

  // Update ref when onMessage changes
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  // Build WebSocket URL
  const socketUrl = useMemo(() => {
    if (!queryId || !enabled) {
      return null
    }
    const path = API_ENDPOINTS.WS.QUERY(queryId)
    return getWebSocketUrl(path)
  }, [queryId, enabled])

  // Use react-use-websocket hook
  const {
    lastMessage: rawLastMessage,
    sendMessage,
    readyState,
  } = useWebSocket(socketUrl, {
    shouldReconnect: () => enabled && queryId !== null,
    reconnectInterval: 3000,
    reconnectAttempts: 10,
    onOpen: () => {
      // Send initial ping
      sendMessage(JSON.stringify({ type: 'ping' }))
    },
    onMessage: (event: MessageEvent) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage
        onMessageRef.current?.(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    },
  })

  // Parse last message
  const lastMessage = useMemo<WebSocketMessage | null>(() => {
    if (!rawLastMessage?.data) {
      return null
    }
    try {
      return JSON.parse(rawLastMessage.data) as WebSocketMessage
    } catch {
      return null
    }
  }, [rawLastMessage])

  // Set up ping interval (every 30 seconds)
  useEffect(() => {
    if (readyState === 1 && queryId) {
      // WebSocket.OPEN = 1
      pingIntervalRef.current = window.setInterval(() => {
        sendMessage(JSON.stringify({ type: 'ping' }))
      }, 30000)
    }

    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current)
        pingIntervalRef.current = null
      }
    }
  }, [readyState, queryId, sendMessage])

  // Map readyState to connection state
  const connectionState = useMemo<
    'connecting' | 'connected' | 'disconnected' | 'error'
  >(() => {
    // WebSocket readyState constants:
    // 0 = CONNECTING
    // 1 = OPEN
    // 2 = CLOSING
    // 3 = CLOSED
    if (readyState === 0) return 'connecting'
    if (readyState === 1) return 'connected'
    if (readyState === 2 || readyState === 3) return 'disconnected'
    return 'error'
  }, [readyState])

  const isConnected = readyState === 1

  return {
    lastMessage,
    sendMessage: (message: object) => {
      sendMessage(JSON.stringify(message))
    },
    readyState,
    isConnected,
    connectionState,
  }
}

