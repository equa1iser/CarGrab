import Link from "next/link";
import { Car } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-white/6 bg-navy-900/50 mt-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/20 border border-cyan-500/30">
                <Car className="h-3.5 w-3.5 text-cyan-400" />
              </div>
              <span className="font-bold text-white">Car<span className="text-cyan-400">Grab</span></span>
            </div>
            <p className="text-sm text-slate-500">
              One place to find the best used car deals across all major sources.
            </p>
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Browse</h3>
            <ul className="space-y-2 text-sm text-slate-500">
              <li><Link href="/search" className="hover:text-cyan-400 transition-colors">Search Cars</Link></li>
              <li><Link href="/search?condition=certified" className="hover:text-cyan-400 transition-colors">Certified Pre-Owned</Link></li>
              <li><Link href="/search?price_max=1500000" className="hover:text-cyan-400 transition-colors">Under $15,000</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-3">Account</h3>
            <ul className="space-y-2 text-sm text-slate-500">
              <li><Link href="/saved" className="hover:text-cyan-400 transition-colors">Saved Searches</Link></li>
              <li><Link href="/saved" className="hover:text-cyan-400 transition-colors">Price Alerts</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-10 pt-6 border-t border-white/6 text-center text-xs text-slate-600">
          © {new Date().getFullYear()} CarGrab. Data sourced from public listings. Not affiliated with CarMax, Carvana, or any other platform.
        </div>
      </div>
    </footer>
  );
}
