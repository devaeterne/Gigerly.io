// web/hooks/use-auth.tsx
'use client'

import { createContext, useContext, useState, useEffect } from 'react'
import { User } from '@/types'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

let userPromise: Promise<User | null> | null = null

async function fetchUserInfo(token: string): Promise<User | null> {
  if (!userPromise) {
    userPromise = fetch('/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
      .then(async (response) => {
        if (response.ok) {
          return response.json()
        }
        localStorage.removeItem('access_token')
        return null
      })
      .catch((error) => {
        console.error('Failed to fetch user info:', error)
        localStorage.removeItem('access_token')
        return null
      })
  }
  return userPromise
}

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUserInfo(token).then((userData) => {
        if (userData) {
          setUser(userData)
        }
        setIsLoading(false)
      })
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    if (response.ok) {
      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      userPromise = Promise.resolve(data.user)
      setUser(data.user)
      return { success: true }
    } else {
      const error = await response.json()
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    userPromise = null
    setUser(null)
  }

  const value: AuthContextValue = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
