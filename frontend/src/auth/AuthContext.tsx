import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

import * as authApi from '../api/auth';
import { setUnauthorizedHandler } from '../api/client';
import type { User } from '../api/types';
import { clearToken, getToken, setToken } from './token';

interface AuthContextValue {
  user: User | null;
  /** True while we check whether a stored token is still valid on startup. */
  initializing: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(() => getToken() !== null);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  // Validate a stored token on startup, and log out on any 401 thereafter.
  useEffect(() => {
    setUnauthorizedHandler(logout);
    if (getToken()) {
      authApi
        .me()
        .then(setUser)
        .catch(() => logout())
        .finally(() => setInitializing(false));
    }
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    setToken(response.token);
    setUser(response.user);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const response = await authApi.register(email, password);
    setToken(response.token);
    setUser(response.user);
  }, []);

  return (
    <AuthContext.Provider value={{ user, initializing, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (value === null) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return value;
}
