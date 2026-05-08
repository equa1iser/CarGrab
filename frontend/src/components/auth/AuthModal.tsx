"use client";

import { useEffect, useRef, useState } from "react";
import { X, Car, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth, registerModalHandlers } from "@/lib/auth-context";

type Mode = "signin" | "register";

export function AuthModal() {
  const { login, register } = useAuth();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);

  // Register open handlers so AuthContext can trigger the modal.
  useEffect(() => {
    registerModalHandlers(
      () => { setMode("signin"); setOpen(true); },
      () => { setMode("register"); setOpen(true); }
    );
  }, []);

  // Auto-focus email when modal opens.
  useEffect(() => {
    if (open) {
      setTimeout(() => emailRef.current?.focus(), 50);
    } else {
      setEmail("");
      setPassword("");
      setConfirm("");
      setError(null);
    }
  }, [open]);

  // Close on Escape.
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (mode === "register" && password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      if (mode === "signin") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      setOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      // Surface friendly messages for common API errors.
      if (msg.includes("401") || msg.includes("Incorrect")) {
        setError("Incorrect email or password.");
      } else if (msg.includes("409") || msg.includes("already")) {
        setError("An account with that email already exists.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-navy-950/80 backdrop-blur-sm" />

      {/* Modal */}
      <div className="relative w-full max-w-sm glass rounded-2xl p-8 shadow-[0_24px_64px_rgba(0,0,0,0.6)] border border-white/8">
        {/* Close */}
        <button
          onClick={() => setOpen(false)}
          className="absolute top-4 right-4 p-1.5 text-slate-500 hover:text-white transition-colors rounded-lg hover:bg-white/5"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Logo mark */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 border border-cyan-500/25 mb-5">
          <Car className="h-5 w-5 text-cyan-400" />
        </div>

        {/* Heading */}
        <h2 className="text-xl font-bold text-white mb-1">
          {mode === "signin" ? "Welcome back" : "Create your account"}
        </h2>
        <p className="text-sm text-slate-400 mb-6">
          {mode === "signin"
            ? "Sign in to access saved searches and price alerts."
            : "Start saving searches and get notified when prices drop."}
        </p>

        {/* Tab toggle */}
        <div className="flex rounded-lg border border-white/8 p-1 mb-6 bg-navy-900/50">
          {(["signin", "register"] as Mode[]).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setError(null); }}
              className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                mode === m
                  ? "bg-cyan-500 text-navy-900 shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {m === "signin" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            ref={emailRef}
            id="auth-email"
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
          <Input
            id="auth-password"
            label="Password"
            type="password"
            placeholder={mode === "register" ? "At least 8 characters" : "••••••••"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete={mode === "signin" ? "current-password" : "new-password"}
          />
          {mode === "register" && (
            <Input
              id="auth-confirm"
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              autoComplete="new-password"
            />
          )}

          {error && (
            <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" className="w-full mt-2" disabled={loading}>
            {loading ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> {mode === "signin" ? "Signing in…" : "Creating account…"}</>
            ) : mode === "signin" ? (
              "Sign In"
            ) : (
              "Create Account"
            )}
          </Button>
        </form>

        <p className="text-xs text-slate-500 text-center mt-4">
          {mode === "signin" ? (
            <>Don&apos;t have an account?{" "}
              <button onClick={() => { setMode("register"); setError(null); }} className="text-cyan-400 hover:text-cyan-300 transition-colors">
                Create one
              </button>
            </>
          ) : (
            <>Already have an account?{" "}
              <button onClick={() => { setMode("signin"); setError(null); }} className="text-cyan-400 hover:text-cyan-300 transition-colors">
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
