"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  ReactNode,
} from "react";
import { login as apiLogin, register as apiRegister, googleAuth as apiGoogleAuth } from "@/lib/api";
import { User } from "@/types";

interface AuthState {
  user: User | null;
  token: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  logout: () => void;
  openSignIn: () => void;
  openRegister: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

// Callbacks registered by the modal so the provider can open it.
const _openHandlers = {
  signIn: null as (() => void) | null,
  register: null as (() => void) | null,
};

export function registerModalHandlers(
  signIn: () => void,
  register: () => void
) {
  _openHandlers.signIn = signIn;
  _openHandlers.register = register;
}

const STORAGE_KEY = "cg_auth";

function loadStored(): AuthState {
  if (typeof window === "undefined") return { user: null, token: null };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { user: null, token: null };
    return JSON.parse(raw) as AuthState;
  } catch {
    return { user: null, token: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({ user: null, token: null });
  const initialized = useRef(false);

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      setAuth(loadStored());
    }
  }, []);

  const persist = useCallback((state: AuthState) => {
    setAuth(state);
    if (state.token) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await apiLogin(email, password);
      persist({ user: res.user, token: res.access_token });
    },
    [persist]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await apiRegister(email, password);
      persist({ user: res.user, token: res.access_token });
    },
    [persist]
  );

  const googleLogin = useCallback(
    async (credential: string) => {
      const res = await apiGoogleAuth(credential);
      persist({ user: res.user, token: res.access_token });
    },
    [persist]
  );

  const logout = useCallback(() => {
    persist({ user: null, token: null });
  }, [persist]);

  const openSignIn = useCallback(() => {
    _openHandlers.signIn?.();
  }, []);

  const openRegister = useCallback(() => {
    _openHandlers.register?.();
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, login, register, googleLogin, logout, openSignIn, openRegister }}>
      {children}
    </AuthContext.Provider>
  );
}
