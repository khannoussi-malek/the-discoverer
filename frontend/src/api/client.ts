/**
 * Axios API client with interceptors
 */

import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { env } from '@/config/env'

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add API key if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add API key from env or localStorage
    const apiKey = env.apiKey || localStorage.getItem('api_key')
    if (apiKey) {
      config.headers['X-API-Key'] = apiKey
    }
    
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('api_key')
      // Could redirect to login page here
    }
    
    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('Access forbidden')
    }
    
    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('Server error occurred')
    }
    
    return Promise.reject(error)
  }
)

export default apiClient

