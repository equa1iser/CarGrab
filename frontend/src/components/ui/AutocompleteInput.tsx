"use client";

import { useEffect, useRef, useState } from "react";
import { getSearchSuggestions } from "@/lib/api";

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

interface Props {
  field: "make" | "model";
  placeholder?: string;
  value: string;
  onValueChange: (value: string) => void;
}

export function AutocompleteInput({ field, placeholder, value, onValueChange }: Props) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debouncedValue = useDebounce(value, 280);

  useEffect(() => {
    if (debouncedValue.length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }
    getSearchSuggestions(debouncedValue)
      .then((r) => {
        const results = (field === "make" ? r.makes : r.models).slice(0, 8);
        setSuggestions(results);
        setShowDropdown(results.length > 0);
        setActiveIdx(-1);
      })
      .catch(() => setSuggestions([]));
  }, [debouncedValue, field]);

  useEffect(() => {
    if (!showDropdown) return;
    const handler = (e: MouseEvent) => {
      if (
        !inputRef.current?.contains(e.target as Node) &&
        !dropdownRef.current?.contains(e.target as Node)
      ) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [showDropdown]);

  function select(s: string) {
    onValueChange(s);
    setShowDropdown(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!showDropdown || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIdx((i) => Math.min(i + 1, suggestions.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIdx((i) => Math.max(i - 1, -1));
    } else if (e.key === "Enter" && activeIdx >= 0) {
      e.preventDefault();
      select(suggestions[activeIdx]);
    } else if (e.key === "Escape") {
      setShowDropdown(false);
    }
  }

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => { onValueChange(e.target.value); setShowDropdown(true); }}
        onFocus={() => suggestions.length > 0 && setShowDropdown(true)}
        onKeyDown={handleKeyDown}
        className="w-full bg-navy-800/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-300 placeholder:text-slate-500 outline-none focus:border-cyan-500/40 transition-colors"
      />
      {showDropdown && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute left-0 right-0 top-full mt-1 glass rounded-xl border border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.5)] z-[200]"
        >
          {suggestions.map((s, i) => (
            <button
              key={s}
              type="button"
              onMouseDown={() => select(s)}
              className={`w-full text-left px-3 py-2 text-sm transition-colors ${
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
  );
}
