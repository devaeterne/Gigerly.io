// # web/types/index.ts
export interface User {
  id: number
  email: string
  role: 'admin' | 'moderator' | 'helpdesk' | 'freelancer' | 'customer'
  status: 'active' | 'inactive' | 'suspended' | 'banned'
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  profile?: UserProfile
}

export interface UserProfile {
  id: number
  user_id: number
  display_name?: string
  first_name?: string
  last_name?: string
  title?: string
  bio?: string
  skills: Skill[]
  hourly_rate?: number
  currency: string
  country?: string
  city?: string
  avatar_url?: string
  total_earnings: number
  completed_projects: number
  average_rating?: number
  total_reviews: number
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface Skill {
  name: string
  level?: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert'
  years_experience?: number
  required?: boolean
}

export interface Project {
  id: number
  title: string
  description: string
  customer_id: number
  budget_type: 'fixed' | 'hourly'
  budget_min?: number
  budget_max?: number
  hourly_rate_min?: number
  hourly_rate_max?: number
  currency: string
  complexity?: 'simple' | 'intermediate' | 'complex'
  deadline?: string
  status: 'draft' | 'open' | 'in_progress' | 'completed' | 'cancelled' | 'closed'
  category?: string
  required_skills: Skill[]
  proposal_count: number
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  error?: string
}