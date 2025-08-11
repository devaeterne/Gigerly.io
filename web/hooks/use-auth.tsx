// web/hooks/use-auth.tsx
"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { User } from "@/types";

const TOKEN_COOKIE = "access_token";

function setAuthCookie(token: string) {
  document.cookie = `${TOKEN_COOKIE}=${token}; Path=/; Secure; SameSite=Strict; HttpOnly`;
}

function clearAuthCookie() {
  document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; Secure; SameSite=Strict; HttpOnly`;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

let userPromise: Promise<User | null> | null = null;

async function fetchUserInfo(): Promise<User | null> {
  if (!userPromise) {
    userPromise = fetch("/api/v1/auth/me", {
      credentials: "include",
    })
      .then(async (response) => {
        if (response.ok) {
          return response.json();
        }
        clearAuthCookie();
        return null;
      })
      .catch((error) => {
        console.error("Failed to fetch user info:", error);
        clearAuthCookie();
        return null;
      });
  }
  return userPromise;
}

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUserInfo().then((userData) => {
      if (userData) {
        setUser(userData);
      }
      setIsLoading(false);
    });
  }, []);

  const login = async (email: string, password: string) => {
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    });

    if (response.ok) {
      userPromise = fetchUserInfo();
      const userData = await userPromise;
      setUser(userData);
      return { success: true };
    } else {
      const error = await response.json();
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    clearAuthCookie();
    userPromise = null;
    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}