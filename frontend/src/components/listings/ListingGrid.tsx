import { ListingCard } from "@/components/listings/ListingCard";
import { ListingCard as ListingCardType } from "@/types";

interface Props {
  listings: ListingCardType[];
  emptyMessage?: string;
}

export function ListingGrid({ listings, emptyMessage = "No listings found." }: Props) {
  if (listings.length === 0) {
    return (
      <div className="py-20 text-center text-slate-500">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      {listings.map((listing, index) => (
        <ListingCard
          key={listing.id}
          listing={listing}
          animationDelay={index * 60}
        />
      ))}
    </div>
  );
}

export function ListingGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="glass rounded-xl overflow-hidden">
          <div className="aspect-video shimmer" />
          <div className="p-4 space-y-3">
            <div className="h-7 w-28 rounded shimmer" />
            <div className="h-4 w-3/4 rounded shimmer" />
            <div className="space-y-2">
              <div className="h-3 w-1/2 rounded shimmer" />
              <div className="h-3 w-2/5 rounded shimmer" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
