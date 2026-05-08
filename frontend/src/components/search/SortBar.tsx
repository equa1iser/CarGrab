"use client";

import { SearchParams } from "@/types";
import { SlidersHorizontal } from "lucide-react";

interface Props {
  total: number;
  filters: SearchParams;
  onChange: (filters: SearchParams) => void;
  onOpenFilters?: () => void;
}

const SORT_OPTIONS = [
  { value: "newest", label: "Newest" },
  { value: "price_asc", label: "Price: Low → High" },
  { value: "price_desc", label: "Price: High → Low" },
  { value: "mileage_asc", label: "Lowest Mileage" },
];

export function SortBar({ total, filters, onChange, onOpenFilters }: Props) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        {onOpenFilters && (
          <button
            onClick={onOpenFilters}
            className="md:hidden flex items-center gap-1.5 glass rounded-lg px-3 py-2 text-sm text-slate-300 hover:text-white"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Filters
          </button>
        )}
        <p className="text-sm text-slate-400">
          <span className="text-white font-semibold">{total.toLocaleString()}</span> listings
        </p>
      </div>
      <select
        value={filters.sort ?? "newest"}
        onChange={(e) => onChange({ ...filters, sort: e.target.value, page: 1 })}
        className="bg-navy-800/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 outline-none focus:border-cyan-500/40"
      >
        {SORT_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}
