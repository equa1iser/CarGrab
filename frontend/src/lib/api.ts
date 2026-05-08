import { ListingCard, ListingDetail, PaginatedListings, SavedSearch, SearchParams, User } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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

export function getSearchFacets(): Promise<{
  makes: { value: string; count: number }[];
  states: { value: string; count: number }[];
  conditions: { value: string; count: number }[];
}> {
  return request("/api/v1/search/facets");
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

export function deleteSavedSearch(token: string, id: string): Promise<void> {
  return request(`/api/v1/saved-searches/${id}`, {
    method: "DELETE",
    headers: authHeader(token),
  });
}
