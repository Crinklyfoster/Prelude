"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { getCurrentUser, login as loginApi, register as registerApi } from "@/lib/api/auth";
import { getToken, removeToken, saveToken } from "@/lib/auth";
import type { AuthContextType, User } from "@/types/auth";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [user, setUser] = useState<User | null>(null);

  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = getToken();

    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const currentUser = await getCurrentUser();

      setUser(currentUser);
    } catch {
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    (async () => {
      await loadUser();
      if (!isMounted) return;
    })();

    return () => {
      isMounted = false;
    };
  }, [loadUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await loginApi({
        email,
        password,
      });

      saveToken(token.access_token);

      const currentUser = await getCurrentUser();

      setUser(currentUser);
    },
    []
  );

  const register = useCallback(
    async (
      name: string,
      email: string,
      password: string
    ) => {
      await registerApi({
        name,
        email,
        password,
      });

      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    removeToken();

    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,

      loading,

      isAuthenticated: user !== null,

      login,

      register,

      logout,
    }),
    [
      user,
      loading,
      login,
      register,
      logout,
    ]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}