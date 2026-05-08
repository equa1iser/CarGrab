import { notFound } from "next/navigation";
import Link from "next/link";
import { ExternalLink, AlertTriangle, ArrowLeft } from "lucide-react";
import { getListing, searchListings } from "@/lib/api";
import { PhotoGallery } from "@/components/listings/PhotoGallery";
import { SpecTable } from "@/components/listings/SpecTable";
import { PriceHistoryChart } from "@/components/listings/PriceHistoryChart";
import { ListingGrid } from "@/components/listings/ListingGrid";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { formatMileage, formatRelative } from "@/lib/formatters";
import { PriceAlertSection } from "./PriceAlertSection";

export const revalidate = 300;

interface Props {
  params: Promise<{ id: string }>;
}

export default async function ListingDetailPage({ params }: Props) {
  const { id } = await params;

  let listing;
  try {
    listing = await getListing(id);
  } catch {
    notFound();
  }

  let similar: Awaited<ReturnType<typeof searchListings>>["items"] = [];
  try {
    const res = await searchListings({
      make: listing.make ?? undefined,
      model: listing.model ?? undefined,
      sort: "price_asc",
      page_size: 4,
    });
    similar = res.items.filter((l) => l.id !== listing.id).slice(0, 4);
  } catch {
    // non-critical
  }

  return (
    <div className="pt-20 min-h-screen">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Back */}
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Search
        </Link>

        {/* Recall warning */}
        {listing.vehicle && listing.vehicle.recall_count > 0 && (
          <div className="mb-6 flex items-start gap-3 glass border border-amber-500/30 rounded-xl px-4 py-3">
            <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-sm text-amber-400">
              This vehicle has <strong>{listing.vehicle.recall_count}</strong> NHTSA safety recall{listing.vehicle.recall_count > 1 ? "s" : ""} on record.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: gallery + charts */}
          <div className="lg:col-span-2 space-y-6">
            <PhotoGallery photos={listing.photos} title={listing.title} />

            {/* Specs */}
            {listing.vehicle && (
              <GlassCard className="p-6">
                <h2 className="text-sm font-semibold text-white mb-4">Vehicle Specs</h2>
                <SpecTable
                  vehicle={listing.vehicle}
                  mileage={listing.mileage}
                  condition={listing.condition}
                  colorExterior={listing.color_exterior}
                  colorInterior={listing.color_interior}
                />
              </GlassCard>
            )}

            {/* Price history */}
            {listing.price_history.length > 1 && (
              <GlassCard className="p-6">
                <h2 className="text-sm font-semibold text-white mb-4">Price History</h2>
                <PriceHistoryChart data={listing.price_history} />
              </GlassCard>
            )}
          </div>

          {/* Right: price card */}
          <div className="space-y-4">
            <GlassCard className="p-6 space-y-4">
              <div>
                {listing.condition && (
                  <Badge variant={listing.condition === "certified" ? "green" : "default"} className="mb-2 capitalize">
                    {listing.condition}
                  </Badge>
                )}
                <div className="text-price text-3xl font-bold">{listing.price_formatted}</div>
                <h1 className="text-xl font-bold text-white mt-1">
                  {listing.title ?? `${listing.year} ${listing.make} ${listing.model}`}
                </h1>
              </div>

              <div className="space-y-2 text-sm text-slate-400">
                {listing.mileage != null && <div>{formatMileage(listing.mileage)}</div>}
                {listing.location_city && (
                  <div>{[listing.location_city, listing.location_state].filter(Boolean).join(", ")}</div>
                )}
                {listing.dealer_name && <div>{listing.dealer_name}</div>}
                <div className="text-slate-500">Listed {formatRelative(listing.first_seen_at)}</div>
              </div>

              {listing.vin && (
                <div className="pt-2 border-t border-white/6">
                  <p className="text-xs text-slate-500 mb-1">VIN</p>
                  <p className="font-mono text-xs text-slate-300 break-all">{listing.vin}</p>
                </div>
              )}

              <a href={listing.url} target="_blank" rel="noopener noreferrer" className="block">
                <Button className="w-full" size="lg">
                  View on {listing.source_name ?? "Source"}
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </a>

              {listing.source_name && (
                <p className="text-xs text-center text-slate-600">
                  Listing provided by {listing.source_name}
                </p>
              )}
            </GlassCard>

            <PriceAlertSection listingId={listing.id} currentPrice={listing.price} />
          </div>
        </div>

        {/* Similar listings */}
        {similar.length > 0 && (
          <section className="mt-12">
            <h2 className="text-lg font-bold text-white mb-5">Similar Listings</h2>
            <ListingGrid listings={similar} />
          </section>
        )}
      </div>
    </div>
  );
}
