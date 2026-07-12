/**
 * Store d'authentification — Zustand.
 * Gère l'utilisateur courant, le statut d'auth, et l'initialisation au démarrage.
 */
import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthService } from '../services/auth';
import { api } from '../services/api';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  requires2FA: boolean;
  challengeToken: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  set2FAChallenge: (token: string) => void;
  complete2FA: (code: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    requires2FA: false,
    challengeToken: null,
  });

  // Init : check if token exists and fetch user
  useEffect(() => {
    (async () => {
      const token = await api.getAccessToken();
      if (token) {
        try {
          const user = await AuthService.getCurrentUser();
          setState({
            user,
            isLoading: false,
            isAuthenticated: true,
            requires2FA: false,
            challengeToken: null,
          });
        } catch {
          setState(s => ({ ...s, isLoading: false }));
        }
      } else {
        setState(s => ({ ...s, isLoading: false }));
      }
    })();
  }, []);

  const login = async (email: string, password: string) => {
    const result = await AuthService.login(email, password);
    if (result.requires_2fa && result.challenge_token) {
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        requires2FA: true,
        challengeToken: result.challenge_token,
      });
    } else if (result.access) {
      setState({
        user: result.user,
        isLoading: false,
        isAuthenticated: true,
        requires2FA: false,
        challengeToken: null,
      });
    }
  };

  const register = async (data: any) => {
    const result = await AuthService.register(data);
    setState({
      user: result.user,
      isLoading: false,
      isAuthenticated: true,
      requires2FA: false,
      challengeToken: null,
    });
  };

  const logout = async () => {
    await AuthService.logout();
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      requires2FA: false,
      challengeToken: null,
    });
  };

  const refreshUser = async () => {
    const user = await AuthService.getCurrentUser();
    setState(s => ({ ...s, user }));
  };

  const set2FAChallenge = (token: string) => {
    setState(s => ({ ...s, requires2FA: true, challengeToken: token }));
  };

  const complete2FA = async (code: string) => {
    if (!state.challengeToken) return;
    await AuthService.verify2FA(state.challengeToken, code);
    const user = await AuthService.getCurrentUser();
    setState({
      user,
      isLoading: false,
      isAuthenticated: true,
      requires2FA: false,
      challengeToken: null,
    });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, refreshUser, set2FAChallenge, complete2FA }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
