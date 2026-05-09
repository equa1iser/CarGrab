import { AdminStats, AiSearchResult, ListingCard, ListingDetail, ListingStats, PaginatedListings, PriceAlert, SavedSearch, SearchFacets, SearchParams, SourceStatus, User, UserListResponse } from "@/types";

// Server components run inside Docker where `localhost` doesn't reach the
// backend container. Use API_INTERNAL_URL (Docker service name) server-side
// and NEXT_PUBLIC_API_URL (host-accessible) client-side.
const BASE =
  typeof window === "undefined"
    ? (process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

function authHeader(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

// ── Listings ──────────────────────────────────────────────────────────────────

export function getFeatured(): Promise<ListingCard[]> {
  return request("/api/v1/listings/featured");
}

export function searchListings(params: SearchParams): Promise<PaginatedListings> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") {
      qs.set(k, String(v));
    }
  }
  return request(`/api/v1/listings?${qs.toString()}`);
}

export function getListing(id: string): Promise<ListingDetail> {
  return request(`/api/v1/listings/${id}`);
}

// ── Search helpers ────────────────────────────────────────────────────────────

export function getSearchSuggestions(q: string): Promise<{ makes: string[]; models: string[] }> {
  return request(`/api/v1/search/suggestions?q=${encodeURIComponent(q)}`);
}

export function getSearchFacets(): Promise<SearchFacets> {
  return request("/api/v1/search/facets");
}

export function parseAiQuery(query: string): Promise<AiSearchResult> {
  return request("/api/v1/search/ai", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

export function getListingStats(): Promise<ListingStats> {
  return request("/api/v1/listings/stats");
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string) {
  return request<{ access_token: string; refresh_token: string; user: User }>(
    "/api/v1/auth/login",
    { method: "POST", body: JSON.stringify({ email, password }) }
  );
}

export async function register(email: string, password: string) {
  return request<{ access_token: string; refresh_token: string; user: User }>(
    "/api/v1/auth/register",
    { method: "POST", body: JSON.stringify({ email, password }) }
  );
}

export async function googleAuth(credential: string) {
  return request<{ access_token: string; refresh_token: string; user: User }>(
    "/api/v1/auth/google",
    { method: "POST", body: JSON.stringify({ credential }) }
  );
}

export async function forgotPassword(email: string): Promise<void> {
  await request("/api/v1/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token: string, password: string): Promise<void> {
  await request("/api/v1/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, password }),
  });
}

// ── Saved searches ────────────────────────────────────────────────────────────

export function getSavedSearches(token: string): Promise<SavedSearch[]> {
  return request("/api/v1/saved-searches", { headers: authHeader(token) });
}

export function createSavedSearch(
  token: string,
  data: { name?: string; filters: SearchParams; alert_email?: boolean }
): Promise<SavedSearch> {
  return request("/api/v1/saved-searches", {
    method: "POST",
    headers: authHeader(token),
    body: JSON.stringify(data),
  });
}

export function updateSavedSearch(
  token: string,
  id: string,
  data: { alert_email: boolean }
): Promise<SavedSearch> {
  return request(`/api/v1/saved-searches/${id}`, {
    method: "PATCH",
    headers: authHeader(token),
    body: JSON.stringify(data),
  });
}

export function deleteSavedSearch(token: string, id: string): Promise<void> {
  return request(`/api/v1/saved-searches/${id}`, {
    method: "DELETE",
    headers: authHeader(token),
  });
}

// ── Price alerts ──────────────────────────────────────────────────────────────

export function getAlerts(token: string): Promise<PriceAlert[]> {
  return request("/api/v1/alerts", { headers: authHeader(token) });
}

export function createAlert(
  token: string,
  data: { listing_id: string; target_price: number }
): Promise<PriceAlert> {
  return request("/api/v1/alerts", {
    method: "POST",
    headers: authHeader(token),
    body: JSON.stringify(data),
  });
}

export function deleteAlert(token: string, id: string): Promise<void> {
  return request(`/api/v1/alerts/${id}`, {
    method: "DELETE",
    headers: authHeader(token),
  });
}

// ── Admin ─────────────────────────────────────────────────────────────────────

export function getAdminStats(token: string): Promise<AdminStats> {
  return request("/api/v1/admin/stats", { headers: authHeader(token) });
}

export function updateSource(
  token: string,
  id: number,
  data: { is_enabled?: boolean; poll_interval_minutes?: number }
): Promise<SourceStatus> {
  return request(`/api/v1/admin/sources/${id}`, {
    method: "PATCH",
    headers: authHeader(token),
    body: JSON.stringify(data),
  });
}

export function triggerSource(
  token: string,
  id: number
): Promise<{ queued: boolean; source: string }> {
  return request(`/api/v1/admin/sources/${id}/trigger`, {
    method: "POST",
    headers: authHeader(token),
  });
}

export function getAdminUsers(token: string, page = 1): Promise<UserListResponse> {
  return request(`/api/v1/admin/users?page=${page}&page_size=20`, {
    headers: authHeader(token),
  });
}
