"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { YEARS, US_STATES } from "@/lib/formatters";
import { getSearchSuggestions } from "@/lib/api";

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function HeroSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [yearMin, setYearMin] = useState("");
  const [state, setState] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const debouncedQuery = useDebounce(query, 280);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setSuggestions([]);
      return;
    }
    getSearchSuggestions(debouncedQuery)
      .then(({ makes, models }) => {
        const combined = [...makes, ...models].slice(0, 8);
        setSuggestions(combined);
        setShowSuggestions(combined.length > 0);
        setActiveIdx(-1);
      })
      .catch(() => setSuggestions([]));
  }, [debouncedQuery]);

  // Close dropdown on outside click
  useEffect(() => {
    if (!showSuggestions) return;
    const handler = (e: MouseEvent) => {
      if (
        !inputRef.current?.contains(e.target as Node) &&
        !dropdownRef.current?.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [showSuggestions]);

  function selectSuggestion(suggestion: string) {
    setQuery(suggestion);
    setShowSuggestions(false);
    navigate(suggestion);
  }

  function navigate(q: string) {
    const params = new URLSearchParams();
    if (q) params.set("query", q);
    if (yearMin) params.set("year_min", yearMin);
    if (state) params.set("state", state);
    router.push(`/search?${params.toString()}`);
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setShowSuggestions(false);
    navigate(query);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!showSuggestions) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, -1));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      selectSuggestion(suggestions[activeIdx]);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
    }
  }

  return (
    <section className="relative min-h-[70vh] flex flex-col items-center justify-center px-4 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-navy-800/50 via-navy-950 to-navy-950 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 w-full max-w-3xl text-center">
        {/* Headline */}
        <div className="mb-3 inline-flex items-center gap-2 glass rounded-full px-3 py-1.5 text-xs text-cyan-400 border border-cyan-500/20">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
          Live listings from multiple sources
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight">
          Find your next car.<br />
          <span className="text-cyan-400">All in one place.</span>
        </h1>
        <p className="text-slate-400 text-lg mb-10 max-w-xl mx-auto">
          CarGrab aggregates listings from CarMax and more so you never miss a deal.
        </p>

        {/* Search form */}
        <form onSubmit={handleSearch} className="glass rounded-2xl p-3 flex flex-col sm:flex-row gap-2">
          {/* Query input + suggestions */}
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              placeholder="Search make, model, or keyword…"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setShowSuggestions(true); }}
              onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
              onKeyDown={handleKeyDown}
              className="w-full bg-transparent px-4 py-2.5 text-white placeholder:text-slate-500 outline-none text-sm"
            />
            {showSuggestions && suggestions.length > 0 && (
              <div
                ref={dropdownRef}
                className="absolute left-0 right-0 top-full mt-1 glass rounded-xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)] overflow-hidden z-50"
              >
                {suggestions.map((s, i) => (
                  <button
                    key={s}
                    type="button"
                    onMouseDown={() => selectSuggestion(s)}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
                      i === activeIdx
                        ? "bg-cyan-500/15 text-cyan-400"
                        : "text-slate-300 hover:bg-white/5 hover:text-white"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-2">
            <select
              value={yearMin}
              onChange={(e) => setYearMin(e.target.value)}
              className="bg-navy-800/80 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
            >
              <option value="">Year</option>
              {YEARS.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="bg-navy-800/80 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
            >
              <option value="">State</option>
              {US_STATES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <Button type="submit" size="md" className="whitespace-nowrap">
              <Search className="h-4 w-4" />
              Search
            </Button>
          </div>
        </form>

        {/* Quick filters */}
        <div className="mt-5 flex flex-wrap justify-center gap-2">
          {[
            { label: "Under $15K", href: "/search?price_max=1500000" },
            { label: "Under 50K Miles", href: "/search?mileage_max=50000" },
            { label: "Certified Pre-Owned", href: "/search?condition=certified" },
            { label: "SUVs", href: "/search?query=suv" },
            { label: "Trucks", href: "/search?query=truck" },
          ].map(({ label, href }) => (
            <a
              key={label}
              href={href}
              className="px-3 py-1.5 rounded-full glass text-xs text-slate-400 hover:text-cyan-400 hover:border-cyan-400/30 border border-white/8 transition-colors"
            >
              {label}
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
