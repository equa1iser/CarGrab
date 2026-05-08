"use client";

import { useEffect, useRef, useState } from "react";
import { X, Car, Loader2, ArrowLeft, Mail } from "lucide-react";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth, registerModalHandlers } from "@/lib/auth-context";
import { forgotPassword } from "@/lib/api";

type Mode = "signin" | "register" | "forgot" | "forgot-sent";

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

export function AuthModal() {
  const { login, register, googleLogin } = useAuth();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const emailRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    registerModalHandlers(
      () => { setMode("signin"); setOpen(true); },
      () => { setMode("register"); setOpen(true); }
    );
  }, []);

  useEffect(() => {
    if (open) {
      setTimeout(() => emailRef.current?.focus(), 50);
    } else {
      setEmail("");
      setPassword("");
      setConfirm("");
      setError(null);
      setMode("signin");
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open]);

  function friendlyError(msg: string): string {
    if (msg.includes("401") || msg.includes("Invalid credentials")) return "Incorrect email or password.";
    if (msg.includes("409") || msg.includes("already")) return "An account with that email already exists.";
    if (msg.includes("501")) return "Google sign-in is not enabled on this server yet.";
    return msg;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (mode === "register" && password !== confirm) { setError("Passwords do not match."); return; }
    if ((mode === "signin" || mode === "register") && password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    try {
      if (mode === "signin") await login(email, password);
      else if (mode === "register") await register(email, password);
      else if (mode === "forgot") {
        await forgotPassword(email);
        setMode("forgot-sent");
        setLoading(false);
        return;
      }
      setOpen(false);
    } catch (err: unknown) {
      setError(friendlyError(err instanceof Error ? err.message : "Something went wrong."));
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(resp: CredentialResponse) {
    if (!resp.credential) return;
    setError(null);
    setLoading(true);
    try {
      await googleLogin(resp.credential);
      setOpen(false);
    } catch (err: unknown) {
      setError(friendlyError(err instanceof Error ? err.message : "Google sign-in failed."));
    } finally {
      setLoading(false);
    }
  }

  if (!open) return null;

  const isForgot = mode === "forgot" || mode === "forgot-sent";

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
    >
      <div className="absolute inset-0 bg-navy-950/80 backdrop-blur-sm" />

      <div className="relative w-full max-w-sm glass rounded-2xl p-8 shadow-[0_24px_64px_rgba(0,0,0,0.6)] border border-white/8">
        {/* Close */}
        <button
          onClick={() => setOpen(false)}
          className="absolute top-4 right-4 p-1.5 text-slate-500 hover:text-white transition-colors rounded-lg hover:bg-white/5"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Logo */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 border border-cyan-500/25 mb-5">
          <Car className="h-5 w-5 text-cyan-400" />
        </div>

        {/* ── Forgot-sent confirmation ── */}
        {mode === "forgot-sent" && (
          <div className="text-center space-y-4 py-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/10 border border-cyan-500/20 mx-auto">
              <Mail className="h-5 w-5 text-cyan-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Check your email</h2>
            <p className="text-sm text-slate-400">
              If <span className="text-white">{email}</span> is registered, we&apos;ve sent a password
              reset link. It expires in 1 hour.
            </p>
            <p className="text-xs text-slate-500">
              Running locally? Check the backend logs for the reset link.
            </p>
            <button
              onClick={() => { setMode("signin"); setEmail(""); }}
              className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              Back to sign in
            </button>
          </div>
        )}

        {/* ── Forgot password form ── */}
        {mode === "forgot" && (
          <>
            <button
              onClick={() => setMode("signin")}
              className="flex items-center gap-1 text-sm text-slate-400 hover:text-white mb-4 transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" /> Back to sign in
            </button>
            <h2 className="text-xl font-bold text-white mb-1">Forgot password?</h2>
            <p className="text-sm text-slate-400 mb-6">
              Enter your email and we&apos;ll send a reset link.
            </p>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                ref={emailRef}
                id="forgot-email"
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
              {error && (
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Sending…</> : "Send Reset Link"}
              </Button>
            </form>
          </>
        )}

        {/* ── Sign in / Register ── */}
        {!isForgot && (
          <>
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
              {(["signin", "register"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => { setMode(m); setError(null); }}
                  className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
                    mode === m ? "bg-cyan-500 text-navy-900 shadow" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {m === "signin" ? "Sign In" : "Create Account"}
                </button>
              ))}
            </div>

            {/* Google button */}
            {GOOGLE_CLIENT_ID && (
              <>
                <div className="mb-4">
                  {loading ? (
                    <div className="flex items-center justify-center h-10 text-slate-400">
                      <Loader2 className="h-4 w-4 animate-spin mr-2" /> Signing in with Google…
                    </div>
                  ) : (
                    <GoogleLogin
                      onSuccess={handleGoogleSuccess}
                      onError={() => setError("Google sign-in failed. Please try again.")}
                      theme="filled_black"
                      size="large"
                      width="100%"
                      text={mode === "signin" ? "signin_with" : "signup_with"}
                    />
                  )}
                </div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex-1 h-px bg-white/8" />
                  <span className="text-xs text-slate-500">or</span>
                  <div className="flex-1 h-px bg-white/8" />
                </div>
              </>
            )}

            {/* Email / password form */}
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
              <div>
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
                {mode === "signin" && (
                  <button
                    type="button"
                    onClick={() => { setMode("forgot"); setError(null); }}
                    className="mt-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors float-right"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
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
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 clear-both">
                  {error}
                </p>
              )}

              <Button type="submit" className="w-full mt-2 clear-both" disabled={loading}>
                {loading ? (
                  <><Loader2 className="h-4 w-4 animate-spin" /> {mode === "signin" ? "Signing in…" : "Creating account…"}</>
                ) : mode === "signin" ? "Sign In" : "Create Account"}
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
          </>
        )}
      </div>
    </div>
  );
}
