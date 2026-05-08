"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import useSWR from "swr";
import { FilterSidebar } from "@/components/search/FilterSidebar";
import { SortBar } from "@/components/search/SortBar";
import { ListingGrid, ListingGridSkeleton } from "@/components/listings/ListingGrid";
import { Button } from "@/components/ui/Button";
import { searchListings } from "@/lib/api";
import { SearchParams } from "@/types";
import { ChevronLeft, ChevronRight } from "lucide-react";

function paramsFromURL(sp: URLSearchParams): SearchParams {
  return {
    make: sp.get("make") ?? undefined,
    model: sp.get("model") ?? undefined,
    year_min: sp.get("year_min") ? Number(sp.get("year_min")) : undefined,
    year_max: sp.get("year_max") ? Number(sp.get("year_max")) : undefined,
    price_min: sp.get("price_min") ? Number(sp.get("price_min")) : undefined,
    price_max: sp.get("price_max") ? Number(sp.get("price_max")) : undefined,
    mileage_max: sp.get("mileage_max") ? Number(sp.get("mileage_max")) : undefined,
    condition: sp.get("condition") ?? undefined,
    state: sp.get("state") ?? undefined,
    query: sp.get("query") ?? undefined,
    sort: sp.get("sort") ?? "newest",
    page: sp.get("page") ? Number(sp.get("page")) : 1,
  };
}

function buildURL(filters: SearchParams): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== null && v !== "") {
      params.set(k, String(v));
    }
  }
  return `/search?${params.toString()}`;
}

export function SearchPageClient() {
  const router = useRouter();
  const urlParams = useSearchParams();
  const [filters, setFilters] = useState<SearchParams>(() => paramsFromURL(urlParams));
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    setFilters(paramsFromURL(urlParams));
  }, [urlParams]);

  const handleFilterChange = useCallback(
    (newFilters: SearchParams) => {
      setFilters(newFilters);
      router.push(buildURL(newFilters), { scroll: false });
    },
    [router]
  );

  const { data, isLoading } = useSWR(
    ["search", filters],
    () => searchListings(filters),
    { keepPreviousData: true }
  );

  return (
    <div className="pt-20 min-h-screen">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6">
          {/* Sidebar — desktop */}
          <aside className="hidden md:block w-64 shrink-0">
            <div className="sticky top-24">
              <FilterSidebar filters={filters} onChange={handleFilterChange} />
            </div>
          </aside>

          {/* Mobile sidebar overlay */}
          {sidebarOpen && (
            <div className="fixed inset-0 z-40 md:hidden" onClick={() => setSidebarOpen(false)}>
              <div className="absolute inset-0 bg-black/60" />
              <div className="absolute left-0 top-0 bottom-0 w-72 overflow-y-auto p-4 bg-navy-900">
                <FilterSidebar
                  filters={filters}
                  onChange={(f) => { handleFilterChange(f); setSidebarOpen(false); }}
                  onClose={() => setSidebarOpen(false)}
                />
              </div>
            </div>
          )}

          {/* Main content */}
          <div className="flex-1 min-w-0 space-y-5">
            <SortBar
              total={data?.total ?? 0}
              filters={filters}
              onChange={handleFilterChange}
              onOpenFilters={() => setSidebarOpen(true)}
            />

            {isLoading ? (
              <ListingGridSkeleton count={24} />
            ) : (
              <ListingGrid
                listings={data?.items ?? []}
                emptyMessage="No listings match your filters. Try broadening your search."
              />
            )}

            {/* Pagination */}
            {data && data.pages > 1 && (
              <div className="flex items-center justify-center gap-3 pt-4">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={(filters.page ?? 1) <= 1}
                  onClick={() => handleFilterChange({ ...filters, page: (filters.page ?? 1) - 1 })}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <span className="text-sm text-slate-400">
                  Page {filters.page ?? 1} of {data.pages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={(filters.page ?? 1) >= data.pages}
                  onClick={() => handleFilterChange({ ...filters, page: (filters.page ?? 1) + 1 })}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
