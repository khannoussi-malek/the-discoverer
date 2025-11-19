/**
 * Authentication hook
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/api/services/auth'
import { useToast } from '@/components/ui/use-toast'

interface User {
  id: string
  username: string
  email: string
  roles: string[]
  is_active: boolean
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()
  const navigate = useNavigate()

  // Check if user is logged in on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const userData = await authService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // Token invalid or expired
      localStorage.removeItem('auth_token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const response = await authService.login(username, password)
    localStorage.setItem('auth_token', response.access_token)
    setUser(response.user)
    return response
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setUser(null)
    navigate('/login')
    toast({
      title: 'Logged out',
      description: 'You have been logged out successfully',
    })
  }, [navigate, toast])

  const isAuthenticated = !!user

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  }
}

