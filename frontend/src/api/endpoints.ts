/**
 * API endpoint constants
 */

export const API_ENDPOINTS = {
  // Discovery
  DISCOVERY: {
    DATABASES: '/api/discovery/databases',
    DATABASE: (id: string) => `/api/discovery/databases/${id}`,
    SYNC: (id: string) => `/api/discovery/databases/${id}/sync`,
  },

  // Query
  QUERY: {
    EXECUTE: '/api/query/execute',
    ANALYZE: '/api/query/analyze',
    HISTORY: '/api/query/history',
  },

  // Visualization
  VISUALIZATION: {
    GENERATE: '/api/visualization/generate',
    EXPORT: (queryId: string) => `/api/visualization/export/${queryId}`,
  },

  // Dashboards
  DASHBOARDS: {
    LIST: '/api/dashboards',
    CREATE: '/api/dashboards',
    GET: (id: string) => `/api/dashboards/${id}`,
    UPDATE: (id: string) => `/api/dashboards/${id}`,
    DELETE: (id: string) => `/api/dashboards/${id}`,
    RENDER: (id: string) => `/api/dashboards/${id}/render`,
    WIDGETS: (id: string) => `/api/dashboards/${id}/widgets`,
  },

  // Templates
  TEMPLATES: {
    LIST: '/api/templates',
    CREATE: '/api/templates',
    GET: (id: string) => `/api/templates/${id}`,
    UPDATE: (id: string) => `/api/templates/${id}`,
    DELETE: (id: string) => `/api/templates/${id}`,
    EXECUTE: (id: string) => `/api/templates/${id}/execute`,
  },

  // Scheduler
  SCHEDULER: {
    LIST: '/api/scheduler',
    CREATE: '/api/scheduler',
    GET: (id: string) => `/api/scheduler/${id}`,
    UPDATE: (id: string) => `/api/scheduler/${id}`,
    DELETE: (id: string) => `/api/scheduler/${id}`,
    EXECUTE: (id: string) => `/api/scheduler/${id}/execute`,
    PAUSE: (id: string) => `/api/scheduler/${id}/pause`,
    RESUME: (id: string) => `/api/scheduler/${id}/resume`,
  },

  // Export
  EXPORT: {
    QUERY: (queryId: string) => `/api/export/query/${queryId}`,
  },

  // Sharing
  SHARING: {
    LIST: '/api/sharing',
    CREATE: '/api/sharing',
    GET: (token: string) => `/api/sharing/${token}`,
    REVOKE: (id: string) => `/api/sharing/${id}/revoke`,
    DELETE: (id: string) => `/api/sharing/${id}`,
  },

  // Analytics
  ANALYTICS: {
    STATS: '/api/analytics/stats',
    TOP_QUERIES: '/api/analytics/top-queries',
  },

  // Webhooks
  WEBHOOKS: {
    LIST: '/api/webhooks',
    CREATE: '/api/webhooks',
    GET: (id: string) => `/api/webhooks/${id}`,
    UPDATE: (id: string) => `/api/webhooks/${id}`,
    DELETE: (id: string) => `/api/webhooks/${id}`,
    STATS: (id: string) => `/api/webhooks/${id}/stats`,
    TEST: (id: string) => `/api/webhooks/test/${id}`,
  },

  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
  },

  // WebSocket
  WS: {
    QUERY: (queryId: string) => `/api/ws/query/${queryId}`,
    GENERAL: '/api/ws/general',
  },

  // Health
  HEALTH: '/health',
  ROOT: '/',
} as const

