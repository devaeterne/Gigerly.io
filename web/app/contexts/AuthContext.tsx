// contexts/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export type UserRole = 'admin' | 'moderator' | 'customer' | 'freelancer';

export interface User {
  id: number;
  email: string;
  role: UserRole;
  status: string;
  isActive: boolean;
  isVerified: boolean;
  profile?: {
    displayName: string;
    firstName?: string;
    lastName?: string;
    avatar?: string;
    title?: string;
    bio?: string;
  };
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (googleToken: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, role: UserRole) => Promise<void>;
  refreshToken: () => Promise<void>;
  hasRole: (roles: UserRole | UserRole[]) => boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }

    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();

      setToken(data.access_token);
      setUser(data.user);

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('refresh_token', data.refresh_token);

      // Redirect based on role
      redirectToRolePage(data.user.role);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const loginWithGoogle = async (googleToken: string) => {
    try {
      const response = await fetch('/api/v1/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id_token: googleToken }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Google login failed');
      }

      const data = await response.json();

      setToken(data.access_token);
      setUser(data.user);

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('refresh_token', data.refresh_token);

      // Redirect based on role
      redirectToRolePage(data.user.role);
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, role: UserRole) => {
    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, role }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();

      setToken(data.access_token);
      setUser(data.user);

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('refresh_token', data.refresh_token);

      // Redirect based on role
      redirectToRolePage(data.user.role);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('refresh_token');
      router.push('/login');
    }
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();

      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  };

  const hasRole = (roles: UserRole | UserRole[]): boolean => {
    if (!user) return false;

    const allowedRoles = Array.isArray(roles) ? roles : [roles];
    return allowedRoles.includes(user.role);
  };

  const redirectToRolePage = (role: UserRole) => {
    switch (role) {
      case 'admin':
        router.push('/admin');
        break;
      case 'moderator':
        router.push('/moderator');
        break;
      case 'customer':
        router.push('/customer');
        break;
      case 'freelancer':
        router.push('/freelancer');
        break;
      default:
        router.push('/');
    }
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    loginWithGoogle,
    logout,
    register,
    refreshToken,
    hasRole,
    isAuthenticated: !!user && !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Higher-Order Component for protecting routes
interface WithAuthProps {
  allowedRoles?: UserRole[];
  redirectTo?: string;
}

export const withAuth = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithAuthProps = {}
) => {
  const { allowedRoles, redirectTo = '/login' } = options;

  const AuthenticatedComponent: React.FC<P> = (props) => {
    const { user, loading, hasRole } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loading) {
        if (!user) {
          router.push(redirectTo);
          return;
        }

        if (allowedRoles && !hasRole(allowedRoles)) {
          // Redirect to appropriate dashboard based on user role
          switch (user.role) {
            case 'admin':
              router.push('/admin');
              break;
            case 'moderator':
              router.push('/moderator');
              break;
            case 'customer':
              router.push('/customer');
              break;
            case 'freelancer':
              router.push('/freelancer');
              break;
            default:
              router.push('/');
          }
          return;
        }
      }
    }, [user, loading, router]);

    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!user) {
      return null; // Will redirect in useEffect
    }

    if (allowedRoles && !hasRole(allowedRoles)) {
      return null; // Will redirect in useEffect
    }

    return <WrappedComponent {...props} />;
  };

  AuthenticatedComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name})`;

  return AuthenticatedComponent;
};

// Hook for role-based access
export const useRoleAccess = () => {
  const { hasRole } = useAuth();

  return {
    isAdmin: hasRole('admin'),
    isModerator: hasRole(['admin', 'moderator']),
    isCustomer: hasRole('customer'),
    isFreelancer: hasRole('freelancer'),
    canManageUsers: hasRole(['admin', 'moderator']),
    canModeratePlatform: hasRole(['admin', 'moderator']),
  };
};