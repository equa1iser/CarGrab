export interface Photo {
  id: string;
  url: string;
  is_primary: boolean;
  sort_order: number;
}

export interface PriceHistoryPoint {
  price: number;
  price_formatted: string;
  recorded_at: string;
}

export interface Vehicle {
  vin: string;
  year: number | null;
  make: string | null;
  model: string | null;
  trim: string | null;
  body_class: string | null;
  drive_type: string | null;
  fuel_type: string | null;
  engine: string | null;
  doors: number | null;
  seats: number | null;
  recall_count: number;
  decoded_at: string;
}

export interface ListingCard {
  id: string;
  url: string;
  title: string | null;
  price: number | null;
  price_formatted: string;
  mileage: number | null;
  year: number | null;
  make: string | null;
  model: string | null;
  trim: string | null;
  condition: string | null;
  location_city: string | null;
  location_state: string | null;
  dealer_name: string | null;
  source_name: string | null;
  primary_photo_url: string | null;
  first_seen_at: string;
}

export interface ListingDetail extends ListingCard {
  description: string | null;
  color_exterior: string | null;
  color_interior: string | null;
  location_zip: string | null;
  vin: string | null;
  photos: Photo[];
  price_history: PriceHistoryPoint[];
  vehicle: Vehicle | null;
  last_seen_at: string;
}

export interface PaginatedListings {
  items: ListingCard[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface SearchParams {
  make?: string;
  model?: string;
  year_min?: number;
  year_max?: number;
  price_min?: number;
  price_max?: number;
  mileage_max?: number;
  condition?: string;
  state?: string;
  query?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export interface SavedSearch {
  id: string;
  name: string | null;
  filters: SearchParams;
  alert_email: boolean;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}
