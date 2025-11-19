/**
 * Authentication API service
 */

import apiClient from '../client'
import { API_ENDPOINTS } from '../endpoints'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    username: string
    email: string
  }
}

export interface User {
  id: string
  username: string
  email: string
  role?: string
}

export const authService = {
  /**
   * Login user
   */
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials)
    const data = response.data
    if (data.access_token) {
      localStorage.setItem('auth_token', data.access_token)
    }
    return data
  },

  /**
   * Register new user
   */
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, userData)
    const data = response.data
    if (data.access_token) {
      localStorage.setItem('auth_token', data.access_token)
    }
    return data
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT)
    localStorage.removeItem('auth_token')
  },

  /**
   * Get current user
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get(API_ENDPOINTS.AUTH.ME)
    return response.data
  },
}

