import { Suspense } from "react";
import { ListingGridSkeleton } from "@/components/listings/ListingGrid";
import { SearchPageClient } from "./SearchPageClient";

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="pt-20 min-h-screen"><div className="mx-auto max-w-7xl px-4 py-8"><ListingGridSkeleton count={24} /></div></div>}>
      <SearchPageClient />
    </Suspense>
  );
}
