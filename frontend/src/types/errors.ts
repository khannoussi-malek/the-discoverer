/**
 * Error type definitions and type guards
 */

export interface ApiError {
  response?: {
    status?: number
    data?: {
      detail?: string
      message?: string
      error?: string
    }
  }
  message?: string
  code?: string
}

export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error
  )
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.response?.data?.detail || 
           error.response?.data?.message || 
           error.response?.data?.error ||
           error.message || 
           'An error occurred'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}

