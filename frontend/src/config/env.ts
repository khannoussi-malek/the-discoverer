/**
 * Environment configuration
 * Reads and validates environment variables
 */

interface EnvConfig {
  apiBaseUrl: string
  apiKey: string | undefined
  appName: string
  enableAnalytics: boolean
}

function getEnvConfig(): EnvConfig {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const apiKey = import.meta.env.VITE_API_KEY
  const appName = import.meta.env.VITE_APP_NAME || 'The Discoverer'
  const enableAnalytics = import.meta.env.VITE_ENABLE_ANALYTICS === 'true' || false

  // Validate required environment variables
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL is required')
  }

  // Validate URL format
  try {
    new URL(apiBaseUrl)
  } catch {
    throw new Error('VITE_API_BASE_URL must be a valid URL')
  }

  return {
    apiBaseUrl,
    apiKey,
    appName,
    enableAnalytics,
  }
}

export const env = getEnvConfig()

/**
 * Convert HTTP/HTTPS URL to WebSocket URL
 * @param path - WebSocket path (e.g., '/api/ws/query/123')
 * @returns WebSocket URL (ws:// or wss://)
 */
export function getWebSocketUrl(path: string): string {
  const baseUrl = env.apiBaseUrl
  const url = new URL(baseUrl)
  
  // Convert protocol: http -> ws, https -> wss
  const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  
  // Build WebSocket URL
  const wsUrl = `${wsProtocol}//${url.host}${path.startsWith('/') ? path : `/${path}`}`
  
  return wsUrl
}

