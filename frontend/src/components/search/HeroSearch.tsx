"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { YEARS, US_STATES } from "@/lib/formatters";

export function HeroSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [yearMin, setYearMin] = useState("");
  const [state, setState] = useState("");

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query) params.set("query", query);
    if (yearMin) params.set("year_min", yearMin);
    if (state) params.set("state", state);
    router.push(`/search?${params.toString()}`);
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
          <input
            type="text"
            placeholder="Search make, model, or keyword…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent px-4 py-2.5 text-white placeholder:text-slate-500 outline-none text-sm"
          />
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
