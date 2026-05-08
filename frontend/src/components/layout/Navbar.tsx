"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Car, Search, Bookmark, Menu, X, ChevronDown, LogOut, Shield, User } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/lib/auth-context";

export function Navbar() {
  const { user, logout, openSignIn, openRegister } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  // Close user dropdown when clicking outside.
  useEffect(() => {
    if (!userMenuOpen) return;
    const handler = (e: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [userMenuOpen]);

  const initials = user?.email ? user.email[0].toUpperCase() : "";

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
            {user ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen((v) => !v)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 hover:border-cyan-400/30 hover:bg-white/5 transition-all duration-200"
                >
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500/20 border border-cyan-500/30 text-xs font-bold text-cyan-400">
                    {initials}
                  </div>
                  <span className="text-sm text-slate-300 max-w-[120px] truncate">{user.email}</span>
                  <ChevronDown className={`h-3.5 w-3.5 text-slate-500 transition-transform duration-200 ${userMenuOpen ? "rotate-180" : ""}`} />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 top-full mt-2 w-48 glass rounded-xl border border-white/8 shadow-[0_8px_32px_rgba(0,0,0,0.4)] overflow-hidden">
                    <div className="px-4 py-3 border-b border-white/6">
                      <p className="text-xs text-slate-500">Signed in as</p>
                      <p className="text-sm text-white font-medium truncate">{user.email}</p>
                    </div>
                    <Link
                      href="/saved"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <Bookmark className="h-3.5 w-3.5" />
                      Saved Searches
                    </Link>
                    {user?.is_admin && (
                      <Link
                        href="/admin"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2.5 text-sm text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/5 transition-colors"
                      >
                        <Shield className="h-3.5 w-3.5" />
                        Admin
                      </Link>
                    )}
                    <button
                      onClick={() => { logout(); setUserMenuOpen(false); }}
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-colors"
                    >
                      <LogOut className="h-3.5 w-3.5" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={openSignIn}>Sign In</Button>
                <Button size="sm" onClick={openRegister}>Get Started</Button>
              </>
            )}
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden border-t border-white/6 py-4 space-y-1">
            <Link
              href="/search"
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5"
              onClick={() => setMobileOpen(false)}
            >
              <Search className="h-3.5 w-3.5" />
              Search Cars
            </Link>
            <Link
              href="/saved"
              className="flex items-center gap-2 px-3 py-2 text-sm text-slate-400 hover:text-white rounded-lg hover:bg-white/5"
              onClick={() => setMobileOpen(false)}
            >
              <Bookmark className="h-3.5 w-3.5" />
              Saved Searches
            </Link>

            {user ? (
              <div className="pt-2 border-t border-white/6 mt-2">
                <div className="flex items-center gap-2 px-3 py-2">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-cyan-500/20 border border-cyan-500/30 text-xs font-bold text-cyan-400">
                    {initials}
                  </div>
                  <span className="text-sm text-slate-300 truncate">{user.email}</span>
                </div>
                {user?.is_admin && (
                  <Link
                    href="/admin"
                    className="flex items-center gap-2 px-3 py-2 text-sm text-cyan-400 hover:text-cyan-300 rounded-lg hover:bg-cyan-500/5 transition-colors"
                    onClick={() => setMobileOpen(false)}
                  >
                    <Shield className="h-3.5 w-3.5" />
                    Admin
                  </Link>
                )}
                <button
                  onClick={() => { logout(); setMobileOpen(false); }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 rounded-lg hover:bg-red-500/5 transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex gap-2 pt-2">
                <Button variant="ghost" size="sm" className="flex-1" onClick={() => { openSignIn(); setMobileOpen(false); }}>
                  Sign In
                </Button>
                <Button size="sm" className="flex-1" onClick={() => { openRegister(); setMobileOpen(false); }}>
                  Get Started
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
