"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Car, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { resetPassword } from "@/lib/api";

function ResetPasswordForm() {
  const params = useSearchParams();
  const token = params.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  if (!token) {
    return (
      <div className="flex flex-col items-center gap-3 text-center py-4">
        <AlertCircle className="h-10 w-10 text-red-400" />
        <h2 className="text-xl font-bold text-white">Invalid link</h2>
        <p className="text-sm text-slate-400">This reset link is missing its token. Please request a new one.</p>
        <Link href="/" className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors mt-2">
          Back to home
        </Link>
      </div>
    );
  }

  if (done) {
    return (
      <div className="flex flex-col items-center gap-3 text-center py-4">
        <CheckCircle className="h-10 w-10 text-cyan-400" />
        <h2 className="text-xl font-bold text-white">Password updated!</h2>
        <p className="text-sm text-slate-400">Your password has been reset. You can now sign in.</p>
        <Link href="/">
          <Button className="mt-2">Go to CarGrab</Button>
        </Link>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) { setError("Passwords do not match."); return; }
    if (password.length < 8) { setError("Password must be at least 8 characters."); return; }
    setLoading(true);
    try {
      await resetPassword(token, password);
      setDone(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      if (msg.includes("400") || msg.includes("expired")) {
        setError("This reset link has expired or already been used. Please request a new one.");
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h2 className="text-xl font-bold text-white mb-1">Choose a new password</h2>
      <p className="text-sm text-slate-400 mb-6">Must be at least 8 characters.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="rp-password"
          label="New Password"
          type="password"
          placeholder="At least 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
          autoFocus
        />
        <Input
          id="rp-confirm"
          label="Confirm Password"
          type="password"
          placeholder="••••••••"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          required
          autoComplete="new-password"
        />
        {error && (
          <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </p>
        )}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Updating…</> : "Reset Password"}
        </Button>
      </form>
    </>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="pt-20 min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <GlassCard className="p-8">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 border border-cyan-500/25 mb-5">
            <Car className="h-5 w-5 text-cyan-400" />
          </div>
          <Suspense fallback={<div className="text-slate-400 text-sm">Loading…</div>}>
            <ResetPasswordForm />
          </Suspense>
        </GlassCard>
      </div>
    </div>
  );
}
