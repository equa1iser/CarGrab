"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";
import { Bell, Bookmark, ChevronLeft, ChevronRight, Loader2, Sparkles, SlidersHorizontal, X } from "lucide-react";
import { FilterSidebar } from "@/components/search/FilterSidebar";
import { SortBar } from "@/components/search/SortBar";
import { ListingGrid, ListingGridSkeleton } from "@/components/listings/ListingGrid";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { createSavedSearch, getSearchFacets, parseAiQuery, searchListings } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { SearchFacets, SearchParams } from "@/types";

function paramsFromURL(sp: URLSearchParams): SearchParams {
  return {
    make: sp.get("make") ?? undefined,
    model: sp.get("model") ?? undefined,
    year_min: sp.get("year_min") ? Number(sp.get("year_min")) : undefined,
    year_max: sp.get("year_max") ? Number(sp.get("year_max")) : undefined,
    price_min: sp.get("price_min") ? Number(sp.get("price_min")) : undefined,
    price_max: sp.get("price_max") ? Number(sp.get("price_max")) : undefined,
    mileage_max: sp.get("mileage_max") ? Number(sp.get("mileage_max")) : undefined,
    condition: sp.get("condition") ?? undefined,
    state: sp.get("state") ?? undefined,
    query: sp.get("query") ?? undefined,
    sort: sp.get("sort") ?? "newest",
    page: sp.get("page") ? Number(sp.get("page")) : 1,
  };
}

function buildURL(filters: SearchParams): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== null && v !== "") {
      params.set(k, String(v));
    }
  }
  return `/search?${params.toString()}`;
}

function SaveSearchPanel({
  filters,
  onSaved,
  onClose,
}: {
  filters: SearchParams;
  onSaved: () => void;
  onClose: () => void;
}) {
  const { token, openSignIn } = useAuth();
  const toast = useToast();
  const [name, setName] = useState("");
  const [alertEmail, setAlertEmail] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    if (!token) { openSignIn(); return; }
    setSaving(true);
    try {
      await createSavedSearch(token, { name: name || undefined, filters, alert_email: alertEmail });
      toast("Search saved!");
      onSaved();
      onClose();
    } catch {
      toast("Failed to save search.", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="glass rounded-xl border border-white/8 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-white">Save this search</p>
        <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
          <X className="h-4 w-4" />
        </button>
      </div>
      <Input
        placeholder="Name (optional)"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <label className="flex items-center gap-2 cursor-pointer select-none">
        <div
          onClick={() => setAlertEmail((v) => !v)}
          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
            alertEmail ? "bg-cyan-500" : "bg-slate-600"
          }`}
        >
          <span
            className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
              alertEmail ? "translate-x-4" : "translate-x-0.5"
            }`}
          />
        </div>
        <Bell className="h-3.5 w-3.5 text-slate-400" />
        <span className="text-xs text-slate-400">Email me new matches</span>
      </label>
      <div className="flex gap-2">
        <Button size="sm" onClick={handleSave} disabled={saving} className="flex-1">
          {saving ? "Saving…" : "Save"}
        </Button>
        <Button size="sm" variant="ghost" onClick={onClose}>Cancel</Button>
      </div>
    </div>
  );
}

export function SearchPageClient() {
  const router = useRouter();
  const urlParams = useSearchParams();
  const toast = useToast();
  const [filters, setFilters] = useState<SearchParams>(() => paramsFromURL(urlParams));
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [saveOpen, setSaveOpen] = useState(false);
  const [facets, setFacets] = useState<SearchFacets | null>(null);

  // AI mode state
  const [aiMode, setAiMode] = useState(false);
  const [aiQuery, setAiQuery] = useState("");
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    setFilters(paramsFromURL(urlParams));
  }, [urlParams]);

  useEffect(() => {
    getSearchFacets()
      .then(setFacets)
      .catch(() => {});
  }, []);

  const handleFilterChange = useCallback(
    (newFilters: SearchParams) => {
      setFilters(newFilters);
      router.push(buildURL(newFilters), { scroll: false });
    },
    [router]
  );

  async function handleAiSearch() {
    if (!aiQuery.trim()) return;
    setAiLoading(true);
    try {
      const result = await parseAiQuery(aiQuery);
      setAiExplanation(result.explanation);
      handleFilterChange({ ...result.filters, sort: filters.sort, page: 1 });
    } catch {
      toast("AI search failed — check that the backend has an ANTHROPIC_API_KEY set.", "error");
    } finally {
      setAiLoading(false);
    }
  }

  const { data, isLoading } = useSWR(
    ["search", filters],
    () => searchListings(filters),
    { keepPreviousData: true }
  );

  return (
    <div className="pt-20 min-h-screen">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6">
          {/* Sidebar — desktop */}
          <aside className="hidden md:block w-64 shrink-0">
            <div className="sticky top-24">
              <FilterSidebar filters={filters} onChange={handleFilterChange} facets={facets} />
            </div>
          </aside>

          {/* Mobile sidebar overlay */}
          {sidebarOpen && (
            <div className="fixed inset-0 z-40 md:hidden" onClick={() => setSidebarOpen(false)}>
              <div className="absolute inset-0 bg-black/60" />
              <div className="absolute left-0 top-0 bottom-0 w-72 overflow-y-auto p-4 bg-navy-900">
                <FilterSidebar
                  filters={filters}
                  onChange={(f) => { handleFilterChange(f); setSidebarOpen(false); }}
                  onClose={() => setSidebarOpen(false)}
                  facets={facets}
                />
              </div>
            </div>
          )}

          {/* Main content */}
          <div className="flex-1 min-w-0 space-y-4">
            {/* Mode toggle */}
            <div className="flex items-center gap-2">
              <div className="flex gap-1 p-1 glass rounded-lg">
                <button
                  onClick={() => { setAiMode(false); setAiExplanation(null); }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    !aiMode
                      ? "bg-white/10 text-white"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <SlidersHorizontal className="h-3.5 w-3.5" />
                  Filters
                </button>
                <button
                  onClick={() => setAiMode(true)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    aiMode
                      ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  AI Search
                </button>
              </div>
            </div>

            {/* AI Search panel */}
            {aiMode && (
              <div className="glass rounded-xl border border-cyan-500/20 p-4 space-y-3">
                <p className="text-xs text-slate-400">
                  Describe what you&apos;re looking for in plain English — AI will extract the filters automatically.
                </p>
                <textarea
                  rows={2}
                  value={aiQuery}
                  onChange={(e) => setAiQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleAiSearch();
                    }
                  }}
                  placeholder='e.g. "red 4WD truck built before 2022 under $90K with low miles"'
                  className="w-full bg-navy-800/60 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-slate-500 outline-none focus:border-cyan-500/40 resize-none transition-colors"
                />
                <div className="flex items-center gap-3 flex-wrap">
                  <Button
                    size="sm"
                    onClick={handleAiSearch}
                    disabled={aiLoading || !aiQuery.trim()}
                  >
                    {aiLoading ? (
                      <><Loader2 className="h-3.5 w-3.5 animate-spin" /> Thinking…</>
                    ) : (
                      <><Sparkles className="h-3.5 w-3.5" /> Search with AI</>
                    )}
                  </Button>
                  {aiExplanation && (
                    <p className="text-xs text-slate-400 italic flex-1">
                      <span className="text-slate-500">Understood as:</span> {aiExplanation}
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <div className="flex-1">
                <SortBar
                  total={data?.total ?? 0}
                  filters={filters}
                  onChange={handleFilterChange}
                  onOpenFilters={() => setSidebarOpen(true)}
                />
              </div>
              <button
                onClick={() => setSaveOpen((v) => !v)}
                className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-cyan-400 border border-white/10 hover:border-cyan-500/30 rounded-lg transition-colors whitespace-nowrap"
              >
                <Bookmark className="h-3.5 w-3.5" />
                Save Search
              </button>
            </div>

            {saveOpen && (
              <SaveSearchPanel
                filters={filters}
                onSaved={() => {}}
                onClose={() => setSaveOpen(false)}
              />
            )}

            {isLoading ? (
              <ListingGridSkeleton count={24} />
            ) : (
              <ListingGrid
                listings={data?.items ?? []}
                emptyMessage="No listings match your filters. Try broadening your search."
              />
            )}

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="flex items-center justify-center gap-3 pt-4">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={(filters.page ?? 1) <= 1}
                  onClick={() => handleFilterChange({ ...filters, page: (filters.page ?? 1) - 1 })}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <span className="text-sm text-slate-400">
                  Page {filters.page ?? 1} of {data.pages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={(filters.page ?? 1) >= data.pages}
                  onClick={() => handleFilterChange({ ...filters, page: (filters.page ?? 1) + 1 })}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
