"use client";

import { useState } from "react";
import { Bell } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { createAlert } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";

interface Props {
  listingId: string;
  currentPrice: number | null;
}

export function PriceAlertSection({ listingId, currentPrice }: Props) {
  const { user, token, openSignIn } = useAuth();
  const toast = useToast();
  const defaultPrice = currentPrice ? String(Math.floor(currentPrice / 100)) : "";
  const [targetPrice, setTargetPrice] = useState(defaultPrice);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) { openSignIn(); return; }
    const cents = Math.round(parseFloat(targetPrice) * 100);
    if (!cents || cents <= 0) return;
    setSaving(true);
    try {
      await createAlert(token, { listing_id: listingId, target_price: cents });
      setSaved(true);
      toast("Price alert set — we'll email you when it drops!");
    } catch {
      toast("Failed to set price alert.", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <GlassCard className="p-5 space-y-3">
      <div className="flex items-center gap-2">
        <Bell className="h-4 w-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-white">Price Alert</h3>
      </div>
      <p className="text-xs text-slate-400">
        Get emailed when this listing drops below your target price.
      </p>

      {saved ? (
        <p className="text-xs text-emerald-400 font-medium">
          Alert set — you'll be notified by email.
        </p>
      ) : !user ? (
        <Button variant="ghost" size="sm" className="w-full" onClick={openSignIn}>
          Sign in to set alert
        </Button>
      ) : (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm pointer-events-none">$</span>
            <input
              type="number"
              min={1}
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="Target price"
              className="w-full pl-7 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-400/50 transition-colors"
            />
          </div>
          <Button type="submit" size="sm" disabled={saving || !targetPrice}>
            {saving ? "…" : "Set Alert"}
          </Button>
        </form>
      )}
    </GlassCard>
  );
}
