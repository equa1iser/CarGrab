import Image from "next/image";
import Link from "next/link";
import { MapPin, Gauge, Calendar, ExternalLink } from "lucide-react";
import { GlassCard } from "@/components/ui/GlassCard";
import { Badge } from "@/components/ui/Badge";
import { formatMileage, formatRelative } from "@/lib/formatters";
import { ListingCard as ListingCardType } from "@/types";

interface Props {
  listing: ListingCardType;
  animationDelay?: number;
}

export function ListingCard({ listing, animationDelay = 0 }: Props) {
  const sourceBadgeVariant = listing.source_name === "carmax" ? "cyan" : "default";

  return (
    <div
      className="opacity-0"
      style={{ animation: `fadeUp 0.5s ease forwards`, animationDelay: `${animationDelay}ms` }}
    >
      <Link href={`/listing/${listing.id}`} className="block group">
        <GlassCard className="overflow-hidden hover:scale-[1.02] transition-transform duration-300">
          {/* Photo */}
          <div className="relative aspect-video bg-navy-800 overflow-hidden">
            {listing.primary_photo_url ? (
              <Image
                src={listing.primary_photo_url}
                alt={listing.title ?? "Vehicle"}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-500"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                unoptimized
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-slate-600">
                <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            )}
            {/* Source badge */}
            {listing.source_name && (
              <div className="absolute top-2 right-2">
                <Badge variant={sourceBadgeVariant} className="text-xs capitalize backdrop-blur-sm">
                  {listing.source_name}
                </Badge>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-4">
            {/* Price */}
            <div className="text-price text-2xl font-bold mb-1">
              {listing.price_formatted}
            </div>

            {/* Title */}
            <h3 className="text-white font-semibold text-sm leading-snug mb-3 line-clamp-1">
              {listing.title ?? `${listing.year} ${listing.make} ${listing.model}`}
            </h3>

            {/* Details */}
            <div className="space-y-1.5">
              {listing.mileage != null && (
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <Gauge className="h-3 w-3 shrink-0" />
                  {formatMileage(listing.mileage)}
                </div>
              )}
              {(listing.location_city || listing.location_state) && (
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <MapPin className="h-3 w-3 shrink-0" />
                  {[listing.location_city, listing.location_state].filter(Boolean).join(", ")}
                </div>
              )}
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <Calendar className="h-3 w-3 shrink-0" />
                {formatRelative(listing.first_seen_at)}
              </div>
            </div>
          </div>
        </GlassCard>
      </Link>
    </div>
  );
}
