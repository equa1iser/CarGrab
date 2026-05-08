"use client";

import { SearchParams } from "@/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { YEARS, US_STATES, formatPrice } from "@/lib/formatters";
import { X } from "lucide-react";

interface Props {
  filters: SearchParams;
  onChange: (filters: SearchParams) => void;
  onClose?: () => void;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">{title}</h3>
      {children}
    </div>
  );
}

export function FilterSidebar({ filters, onChange, onClose }: Props) {
  function update(patch: Partial<SearchParams>) {
    onChange({ ...filters, ...patch, page: 1 });
  }

  function clear() {
    onChange({ sort: filters.sort, page: 1 });
  }

  const hasFilters = !!(
    filters.make || filters.model || filters.year_min || filters.year_max ||
    filters.price_min || filters.price_max || filters.mileage_max ||
    filters.condition || filters.state
  );

  return (
    <aside className="glass rounded-xl p-5 space-y-6 w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Filters</h2>
        <div className="flex gap-2">
          {hasFilters && (
            <button onClick={clear} className="text-xs text-cyan-400 hover:text-cyan-300">
              Clear all
            </button>
          )}
          {onClose && (
            <button onClick={onClose} className="text-slate-400 hover:text-white md:hidden">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Make */}
      <Section title="Make">
        <Input
          placeholder="e.g. Toyota"
          value={filters.make ?? ""}
          onChange={(e) => update({ make: e.target.value || undefined })}
        />
      </Section>

      {/* Model */}
      <Section title="Model">
        <Input
          placeholder="e.g. Camry"
          value={filters.model ?? ""}
          onChange={(e) => update({ model: e.target.value || undefined })}
        />
      </Section>

      {/* Year range */}
      <Section title="Year">
        <div className="flex gap-2">
          <select
            value={filters.year_min ?? ""}
            onChange={(e) => update({ year_min: e.target.value ? Number(e.target.value) : undefined })}
            className="flex-1 bg-navy-800/60 border border-white/10 rounded-lg px-2 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
          >
            <option value="">From</option>
            {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
          <select
            value={filters.year_max ?? ""}
            onChange={(e) => update({ year_max: e.target.value ? Number(e.target.value) : undefined })}
            className="flex-1 bg-navy-800/60 border border-white/10 rounded-lg px-2 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
          >
            <option value="">To</option>
            {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </Section>

      {/* Price range */}
      <Section title="Price">
        <div className="flex gap-2">
          <Input
            placeholder="Min $"
            type="number"
            value={filters.price_min != null ? filters.price_min / 100 : ""}
            onChange={(e) => update({ price_min: e.target.value ? Number(e.target.value) * 100 : undefined })}
          />
          <Input
            placeholder="Max $"
            type="number"
            value={filters.price_max != null ? filters.price_max / 100 : ""}
            onChange={(e) => update({ price_max: e.target.value ? Number(e.target.value) * 100 : undefined })}
          />
        </div>
        {(filters.price_min || filters.price_max) && (
          <p className="text-xs text-slate-500">
            {formatPrice(filters.price_min ?? null)} – {formatPrice(filters.price_max ?? null)}
          </p>
        )}
      </Section>

      {/* Mileage */}
      <Section title="Max Mileage">
        <Input
          placeholder="e.g. 50000"
          type="number"
          value={filters.mileage_max ?? ""}
          onChange={(e) => update({ mileage_max: e.target.value ? Number(e.target.value) : undefined })}
        />
      </Section>

      {/* Condition */}
      <Section title="Condition">
        <div className="flex flex-wrap gap-2">
          {["used", "certified", "salvage"].map((c) => (
            <button
              key={c}
              onClick={() => update({ condition: filters.condition === c ? undefined : c })}
              className={`px-3 py-1.5 rounded-lg text-xs border transition-colors capitalize ${
                filters.condition === c
                  ? "border-cyan-500/60 bg-cyan-500/10 text-cyan-400"
                  : "border-white/10 text-slate-400 hover:border-white/20 hover:text-white"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </Section>

      {/* State */}
      <Section title="State">
        <select
          value={filters.state ?? ""}
          onChange={(e) => update({ state: e.target.value || undefined })}
          className="w-full bg-navy-800/60 border border-white/10 rounded-lg px-2 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
        >
          <option value="">All States</option>
          {US_STATES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </Section>
    </aside>
  );
}
