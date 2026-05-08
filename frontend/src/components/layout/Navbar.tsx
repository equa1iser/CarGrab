"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Car, Search, Bookmark, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/Button";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "glass border-b border-white/6" : "bg-transparent"
      }`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/20 border border-cyan-500/30 group-hover:bg-cyan-500/30 transition-colors">
              <Car className="h-4 w-4 text-cyan-400" />
            </div>
            <span className="text-lg font-bold text-white">
              Car<span className="text-cyan-400">Grab</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              href="/search"
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
            >
              <Search className="h-3.5 w-3.5" />
              Search
            </Link>
            <Link
              href="/saved"
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
            >
              <Bookmark className="h-3.5 w-3.5" />
              Saved
            </Link>
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" size="sm">Sign In</Button>
            <Button size="sm">Get Started</Button>
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setOpen(!open)}
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {open && (
          <div className="md:hidden border-t border-white/6 py-4 space-y-1">
            <Link href="/search" className="block px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5" onClick={() => setOpen(false)}>
              Search Cars
            </Link>
            <Link href="/saved" className="block px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5" onClick={() => setOpen(false)}>
              Saved Searches
            </Link>
            <div className="flex gap-2 pt-2">
              <Button variant="ghost" size="sm" className="flex-1">Sign In</Button>
              <Button size="sm" className="flex-1">Get Started</Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
