"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Shield, RefreshCw, Play, AlertCircle, Check, X, Clock } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { useAuth } from "@/lib/auth-context";
import { getAdminStats, getAdminUsers, triggerSource, updateSource } from "@/lib/api";
import { formatDate, formatRelative } from "@/lib/formatters";
import { AdminStats, SourceStatus, UserSummary } from "@/types";

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatAgo(iso: string | null): string {
  if (!iso) return "Never";
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return formatRelative(iso);
}

function orchestratorColor(iso: string | null): string {
  if (!iso) return "text-red-400";
  const mins = (Date.now() - new Date(iso).getTime()) / 60_000;
  if (mins < 5) return "text-emerald-400";
  if (mins < 15) return "text-amber-400";
  return "text-red-400";
}

function sourceDotColor(s: SourceStatus): string {
  if (!s.is_enabled) return "bg-slate-500";
  if (s.api_key_configured) return "bg-emerald-400";
  return "bg-amber-400";
}

// ── Stat card ─────────────────────────────────────────────────────────────────

function StatCard({ label, value, accent }: { label: string; value: number | string; accent?: boolean }) {
  return (
    <GlassCard className="p-5">
      <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`font-mono text-2xl font-bold ${accent ? "text-cyan-400" : "text-white"}`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
    </GlassCard>
  );
}

// ── Source row ────────────────────────────────────────────────────────────────

function SourceRow({
  source,
  token,
  onUpdated,
}: {
  source: SourceStatus;
  token: string;
  onUpdated: (updated: SourceStatus) => void;
}) {
  const [intervalVal, setIntervalVal] = useState(String(source.poll_interval_minutes));
  const [triggering, setTriggering] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(false);

  const handleToggle = async () => {
    setToggling(true);
    try {
      const updated = await updateSource(token, source.id, { is_enabled: !source.is_enabled });
      onUpdated(updated);
    } catch {
      // silent — the row will stay as-is
    } finally {
      setToggling(false);
    }
  };

  const handleSaveInterval = async () => {
    const parsed = parseInt(intervalVal, 10);
    if (!parsed || parsed < 1) return;
    setSaving(true);
    try {
      const updated = await updateSource(token, source.id, { poll_interval_minutes: parsed });
      onUpdated(updated);
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      await triggerSource(token, source.id);
    } catch {
      // silent
    } finally {
      setTimeout(() => setTriggering(false), 1500);
    }
  };

  return (
    <tr className="border-b border-white/5 hover:bg-white/2 transition-colors">
      {/* Name + status dot */}
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full flex-shrink-0 ${sourceDotColor(source)}`} />
          <span className="text-sm font-medium text-white capitalize">{source.name}</span>
        </div>
      </td>

      {/* API key */}
      <td className="px-4 py-3">
        {source.api_key_configured ? (
          <Badge variant="green">
            <Check className="h-2.5 w-2.5" />
            Configured
          </Badge>
        ) : (
          <Badge className="bg-red-500/15 text-red-400 border-red-500/30">
            <X className="h-2.5 w-2.5" />
            Not Set
          </Badge>
        )}
      </td>

      {/* Poll interval */}
      <td className="px-4 py-3">
        <div className="flex items-center gap-1.5">
          <input
            type="number"
            min={1}
            value={intervalVal}
            onChange={(e) => setIntervalVal(e.target.value)}
            className="w-16 rounded-md bg-white/5 border border-white/10 text-white text-sm px-2 py-1 focus:outline-none focus:border-cyan-400/50"
          />
          <span className="text-xs text-slate-500">min</span>
          <button
            onClick={handleSaveInterval}
            disabled={saving}
            className="text-xs text-cyan-400 hover:text-cyan-300 disabled:opacity-50 transition-colors"
          >
            {saving ? <Spinner className="h-3 w-3" /> : "Save"}
          </button>
        </div>
      </td>

      {/* Enabled toggle */}
      <td className="px-4 py-3">
        <button
          onClick={handleToggle}
          disabled={toggling}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-200 focus:outline-none disabled:opacity-50 ${
            source.is_enabled ? "bg-cyan-500" : "bg-slate-600"
          }`}
        >
          <span
            className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform duration-200 ${
              source.is_enabled ? "translate-x-4" : "translate-x-0.5"
            }`}
          />
        </button>
      </td>

      {/* Last polled */}
      <td className="px-4 py-3 text-xs text-slate-400 font-mono">
        {formatAgo(source.last_polled)}
      </td>

      {/* Listings count */}
      <td className="px-4 py-3 text-xs text-slate-300 font-mono">
        {source.listing_count.toLocaleString()}
      </td>

      {/* Total ingested */}
      <td className="px-4 py-3 text-xs text-slate-400 font-mono">
        {source.total_listings_ingested.toLocaleString()}
      </td>

      {/* Poll Now */}
      <td className="px-4 py-3">
        <button
          onClick={handleTrigger}
          disabled={triggering || !source.api_key_configured}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-cyan-400 disabled:opacity-40 transition-colors"
          title={!source.api_key_configured ? "API key not configured" : "Dispatch poll task now"}
        >
          {triggering ? <Spinner className="h-3 w-3" /> : <Play className="h-3 w-3" />}
          Poll Now
        </button>
      </td>

      {/* Error */}
      <td className="px-4 py-3 max-w-[180px]">
        {source.last_error ? (
          <p className="text-xs text-red-400 truncate" title={source.last_error}>
            <AlertCircle className="inline h-3 w-3 mr-1" />
            {source.last_error}
          </p>
        ) : (
          <span className="text-xs text-slate-600">—</span>
        )}
      </td>
    </tr>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function AdminPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [s, u] = await Promise.all([getAdminStats(token), getAdminUsers(token)]);
      setStats(s);
      setUsers(u.users);
      setUsersTotal(u.total);
      setError(null);
      setLastRefresh(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!user?.is_admin || !token) {
      setLoading(false);
      return;
    }
    fetchData();
    intervalRef.current = setInterval(fetchData, 30_000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [user, token, fetchData]);

  const handleSourceUpdated = useCallback((updated: SourceStatus) => {
    setStats((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        sources: prev.sources.map((s) => (s.id === updated.id ? updated : s)),
      };
    });
  }, []);

  // ── Access guards ──────────────────────────────────────────────────────────

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <GlassCard className="p-8 max-w-sm w-full text-center">
          <Shield className="h-10 w-10 text-slate-500 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-white mb-2">Sign in required</h2>
          <p className="text-sm text-slate-400 mb-4">You must be signed in to access this page.</p>
          <Link href="/">
            <Button variant="ghost" size="sm">Go home</Button>
          </Link>
        </GlassCard>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <GlassCard className="p-8 max-w-sm w-full text-center">
          <Shield className="h-10 w-10 text-red-400 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-white mb-2">Access denied</h2>
          <p className="text-sm text-slate-400 mb-4">You do not have admin access.</p>
          <Link href="/">
            <Button variant="ghost" size="sm">Go home</Button>
          </Link>
        </GlassCard>
      </div>
    );
  }

  // ── Loading ────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <GlassCard className="p-8 max-w-sm w-full text-center">
          <AlertCircle className="h-10 w-10 text-red-400 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-white mb-2">Error</h2>
          <p className="text-sm text-red-400 mb-4">{error}</p>
          <Button size="sm" onClick={fetchData}>Retry</Button>
        </GlassCard>
      </div>
    );
  }

  // ── Dashboard ──────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen px-4 sm:px-6 lg:px-8 py-8 pt-24 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/20 border border-cyan-500/30">
            <Shield className="h-5 w-5 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Admin Dashboard</h1>
            {lastRefresh && (
              <p className="text-xs text-slate-500">Last refreshed {formatAgo(lastRefresh.toISOString())} · auto-refreshes every 30s</p>
            )}
          </div>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {/* Orchestrator status */}
      {stats && (
        <div className="mb-6 flex items-center gap-2">
          <Clock className={`h-4 w-4 ${orchestratorColor(stats.orchestrator_last_ran)}`} />
          <span className="text-sm text-slate-400">
            Orchestrator last ran:{" "}
            <span className={`font-mono font-medium ${orchestratorColor(stats.orchestrator_last_ran)}`}>
              {formatAgo(stats.orchestrator_last_ran)}
            </span>
          </span>
        </div>
      )}

      {/* Stats row */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Listings" value={stats.total_listings} accent />
          <StatCard label="Active Listings" value={stats.active_listings} />
          <StatCard label="Total Users" value={stats.total_users} />
          <StatCard label="New Users (24h)" value={stats.new_users_24h} />
        </div>
      )}

      {/* Data Sources */}
      {stats && (
        <GlassCard className="mb-8 overflow-hidden">
          <div className="px-5 py-4 border-b border-white/6">
            <h2 className="text-sm font-semibold text-white">Data Sources</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5">
                  {["Source", "API Key", "Interval", "Enabled", "Last Polled", "Listings", "Total Ingested", "Actions", "Last Error"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-xs font-medium text-slate-500 uppercase tracking-wider whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {stats.sources.map((s) => (
                  <SourceRow
                    key={s.id}
                    source={s}
                    token={token!}
                    onUpdated={handleSourceUpdated}
                  />
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Users */}
      <GlassCard className="overflow-hidden">
        <div className="px-5 py-4 border-b border-white/6 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">
            Recent Users
            {usersTotal > 0 && (
              <span className="ml-2 text-xs font-normal text-slate-500">({usersTotal} total)</span>
            )}
          </h2>
        </div>
        {users.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-slate-500">No users yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5">
                  {["Email", "Joined", "Auth", "Saved Searches", "Status"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-xs font-medium text-slate-500 uppercase tracking-wider whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-white/5 hover:bg-white/2 transition-colors">
                    <td className="px-4 py-3 text-sm text-white">{u.email}</td>
                    <td className="px-4 py-3 text-xs text-slate-400 font-mono whitespace-nowrap">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      {u.has_google ? (
                        <Badge variant="cyan">Google</Badge>
                      ) : (
                        <Badge variant="default">Email</Badge>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400 font-mono">
                      {u.saved_search_count}
                    </td>
                    <td className="px-4 py-3">
                      {u.is_active ? (
                        <Badge variant="green">Active</Badge>
                      ) : (
                        <Badge className="bg-red-500/15 text-red-400 border-red-500/30">Disabled</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
