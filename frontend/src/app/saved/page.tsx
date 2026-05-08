"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Bookmark, Trash2, Search, Lock, Loader2 } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/formatters";
import { getSavedSearches, deleteSavedSearch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { SavedSearch, SearchParams } from "@/types";

export default function SavedPage() {
  const { user, token, openSignIn, openRegister } = useAuth();
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSavedSearches(token);
      setSearches(data);
    } catch {
      setError("Failed to load saved searches.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete(id: string) {
    if (!token) return;
    setSearches((prev) => prev.filter((s) => s.id !== id));
    try {
      await deleteSavedSearch(token, id);
    } catch {
      // Reload if delete failed server-side
      load();
    }
  }

  function buildSearchURL(filters: SearchParams): string {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(filters)) {
      if (v !== undefined && v !== null && v !== "") params.set(k, String(v));
    }
    return `/search?${params.toString()}`;
  }

  function renderFilterChips(filters: SearchParams) {
    const chips: string[] = [];
    if (filters.make) chips.push(filters.make);
    if (filters.model) chips.push(filters.model);
    if (filters.year_min || filters.year_max)
      chips.push(`${filters.year_min ?? "Any"}–${filters.year_max ?? "Any"}`);
    if (filters.price_max)
      chips.push(`Under $${(filters.price_max / 100).toLocaleString()}`);
    if (filters.mileage_max)
      chips.push(`< ${filters.mileage_max.toLocaleString()} mi`);
    if (filters.state) chips.push(filters.state);
    return chips;
  }

  // Not logged in
  if (!user) {
    return (
      <div className="pt-20 min-h-screen flex items-center justify-center px-4">
        <GlassCard className="p-10 max-w-sm w-full text-center space-y-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-500/10 border border-cyan-500/20 mx-auto">
            <Lock className="h-5 w-5 text-cyan-400" />
          </div>
          <h1 className="text-xl font-bold text-white">Sign in to view saved searches</h1>
          <p className="text-sm text-slate-400">
            Create an account to save your searches and receive price alerts.
          </p>
          <Button className="w-full" onClick={openSignIn}>Sign In</Button>
          <Button variant="ghost" className="w-full" onClick={openRegister}>Create Account</Button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="pt-20 min-h-screen">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Bookmark className="h-5 w-5 text-cyan-400" />
            <h1 className="text-2xl font-bold text-white">Saved Searches</h1>
          </div>
          {searches.length > 0 && (
            <span className="text-sm text-slate-500">{searches.length} saved</span>
          )}
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20 text-slate-500">
            <Loader2 className="h-6 w-6 animate-spin mr-2" />
            Loading…
          </div>
        )}

        {error && !loading && (
          <GlassCard className="p-6 text-center text-red-400">
            {error}
            <button onClick={load} className="block mt-2 text-sm text-cyan-400 hover:text-cyan-300 mx-auto">
              Try again
            </button>
          </GlassCard>
        )}

        {!loading && !error && searches.length === 0 && (
          <GlassCard className="p-12 text-center space-y-4">
            <Search className="h-8 w-8 text-slate-500 mx-auto" />
            <p className="text-slate-400">No saved searches yet.</p>
            <Link href="/search">
              <Button variant="ghost">Start searching</Button>
            </Link>
          </GlassCard>
        )}

        {!loading && searches.length > 0 && (
          <div className="space-y-4">
            {searches.map((ss) => {
              const chips = renderFilterChips(ss.filters);
              return (
                <GlassCard key={ss.id} className="p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white text-sm">
                          {ss.name ?? "Unnamed search"}
                        </h3>
                        {ss.alert_email && (
                          <Badge variant="cyan" className="text-xs">Email alerts on</Badge>
                        )}
                      </div>
                      {chips.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                          {chips.map((chip) => (
                            <Badge key={chip}>{chip}</Badge>
                          ))}
                        </div>
                      )}
                      <p className="text-xs text-slate-500">Saved {formatDate(ss.created_at)}</p>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Link href={buildSearchURL(ss.filters)}>
                        <Button variant="ghost" size="sm">
                          <Search className="h-3.5 w-3.5" />
                          Run
                        </Button>
                      </Link>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(ss.id)}
                        aria-label="Delete saved search"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                </GlassCard>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
