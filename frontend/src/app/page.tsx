import { HeroSearch } from "@/components/search/HeroSearch";
import { ListingGrid, ListingGridSkeleton } from "@/components/listings/ListingGrid";
import { getFeatured, searchListings } from "@/lib/api";
import { Suspense } from "react";
import { TrendingDown, Clock, Database } from "lucide-react";

async function FeaturedListings() {
  try {
    const listings = await getFeatured();
    return <ListingGrid listings={listings} emptyMessage="No featured listings yet — check back once data starts loading." />;
  } catch {
    return <p className="text-slate-500 text-sm">Could not load listings. Is the backend running?</p>;
  }
}

async function NewestListings() {
  try {
    const data = await searchListings({ sort: "newest", page_size: 8 });
    return <ListingGrid listings={data.items} emptyMessage="No listings yet." />;
  } catch {
    return null;
  }
}

export default function HomePage() {
  return (
    <div className="pt-16">
      {/* Hero */}
      <HeroSearch />

      {/* Stats banner */}
      <div className="border-y border-white/6 bg-navy-900/30">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap justify-center gap-8 text-center">
            {[
              { icon: Database, label: "Sources", value: "2+" },
              { icon: Clock, label: "Updated", value: "Every 30 min" },
              { icon: TrendingDown, label: "Avg. Savings", value: "vs MSRP" },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-cyan-400" />
                <span className="text-sm text-slate-400">{label}:</span>
                <span className="text-sm font-semibold text-white">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 space-y-16">
        {/* Featured deals */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <TrendingDown className="h-5 w-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white">Featured Deals</h2>
          </div>
          <Suspense fallback={<ListingGridSkeleton count={8} />}>
            <FeaturedListings />
          </Suspense>
        </section>

        {/* Newest */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Clock className="h-5 w-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white">Just Listed</h2>
          </div>
          <Suspense fallback={<ListingGridSkeleton count={8} />}>
            <NewestListings />
          </Suspense>
        </section>
      </div>
    </div>
  );
}
