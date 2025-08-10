// web/hooks/use-auth.ts
'use client'

import { useState, useEffect } from 'react'
import { User } from '@/types'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for stored auth token and validate
    const token = localStorage.getItem('access_token')
    if (token) {
      // Validate token and get user info
      fetchUserInfo(token)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem('access_token')
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      localStorage.removeItem('access_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      setUser(data.user)
      return { success: true }
    } else {
      const error = await response.json()
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user
  }
}