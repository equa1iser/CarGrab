"""
Rule-based natural language parser for car search queries.
Used as a fallback when no AI API key is configured.
Handles common patterns: prices, years, mileage, makes, colors, drivetrains, body styles.
"""
import re

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

_COMMON_MAKES: set[str] = {
    "acura", "alfa romeo", "aston martin", "audi", "bentley", "bmw",
    "buick", "cadillac", "chevrolet", "chevy", "chrysler", "dodge",
    "ferrari", "fiat", "ford", "genesis", "gmc", "honda", "hyundai",
    "infiniti", "jaguar", "jeep", "kia", "lamborghini", "land rover",
    "lexus", "lincoln", "lotus", "maserati", "mazda", "mclaren",
    "mercedes-benz", "mercedes", "mini", "mitsubishi", "nissan",
    "pontiac", "porsche", "ram", "rivian", "rolls-royce", "saab",
    "subaru", "suzuki", "tesla", "toyota", "volkswagen", "vw", "volvo",
}

# Normalize aliases to canonical display names
_MAKE_ALIASES: dict[str, str] = {
    "chevy": "Chevrolet",
    "vw": "Volkswagen",
    "mercedes": "Mercedes-Benz",
}

_COLORS: set[str] = {
    "red", "blue", "black", "white", "silver", "gray", "grey", "green",
    "yellow", "orange", "brown", "purple", "gold", "beige", "maroon",
    "navy", "cream", "teal", "bronze", "champagne",
}

_DRIVETRAINS: set[str] = {
    "4wd", "4x4", "awd", "fwd", "rwd",
    "four-wheel drive", "four wheel drive", "all-wheel drive",
    "all wheel drive", "rear-wheel drive", "front-wheel drive",
}

_BODY_TYPES: set[str] = {
    "truck", "pickup", "suv", "sedan", "coupe", "convertible",
    "hatchback", "wagon", "minivan", "van", "crossover", "roadster",
    "cabriolet", "cabrio",
}

_US_STATES: dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    # Also accept abbreviations directly
    "al": "AL", "ak": "AK", "az": "AZ", "ar": "AR", "ca": "CA", "co": "CO",
    "ct": "CT", "de": "DE", "fl": "FL", "ga": "GA", "hi": "HI", "id": "ID",
    "il": "IL", "in": "IN", "ia": "IA", "ks": "KS", "ky": "KY", "la": "LA",
    "me": "ME", "md": "MD", "ma": "MA", "mi": "MI", "mn": "MN", "ms": "MS",
    "mo": "MO", "mt": "MT", "ne": "NE", "nv": "NV", "nh": "NH", "nj": "NJ",
    "nm": "NM", "ny": "NY", "nc": "NC", "nd": "ND", "oh": "OH", "ok": "OK",
    "or": "OR", "pa": "PA", "ri": "RI", "sc": "SC", "sd": "SD", "tn": "TN",
    "tx": "TX", "ut": "UT", "vt": "VT", "va": "VA", "wa": "WA", "wv": "WV",
    "wi": "WI", "wy": "WY",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_price_cents(raw: str) -> int:
    """'90K' → 9000000, '90,000' → 9000000, '90000' → 9000000."""
    s = raw.strip().lower().replace(",", "").replace("$", "")
    if s.endswith("k"):
        return round(float(s[:-1]) * 1_000 * 100)
    return round(float(s) * 100)


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def rule_based_parse(query: str) -> tuple[dict, str]:
    """
    Parse a natural language car query into structured filters.
    Returns (filters_dict, explanation_string).
    No external dependencies — stdlib only.
    """
    text = query.lower()
    filters: dict = {}

    # ── Years ───────────────────────────────────────────────────────────────

    # "2018-2022" or "2018 to 2022" (explicit range)
    m = re.search(r'\b((?:19|20)\d{2})\s*(?:to|-)\s*((?:19|20)\d{2})\b', text)
    if m:
        filters["year_min"] = int(m.group(1))
        filters["year_max"] = int(m.group(2))
    else:
        # Upper bound: "before/until/prior to/pre-2022"
        m = re.search(
            r'\b(?:before|prior to|until|up to|no later than|pre[-\s]?)\s*((?:19|20)\d{2})\b',
            text,
        )
        if m:
            filters["year_max"] = int(m.group(1))

        # Lower bound: "after/since/from/newer than 2018"
        m = re.search(
            r'\b(?:after|since|from|newer than|starting|at least)\s*((?:19|20)\d{2})\b',
            text,
        )
        if m:
            filters["year_min"] = int(m.group(1))

    # ── Prices ──────────────────────────────────────────────────────────────

    _price = r'\$?([\d,]+(?:\.\d+)?k?)'

    # Explicit range first: "$20K-$50K" or "$20,000 to $50,000"
    m = re.search(rf'{_price}\s*(?:to|-)\s*{_price}', text, re.I)
    if m:
        filters["price_min"] = _parse_price_cents(m.group(1))
        filters["price_max"] = _parse_price_cents(m.group(2))
    else:
        m = re.search(
            rf'\b(?:under|below|less than|no more than|max(?:imum)?|at most|up to)\s*{_price}',
            text, re.I,
        )
        if m:
            filters["price_max"] = _parse_price_cents(m.group(1))

        m = re.search(
            rf'\b(?:over|above|more than|at least|minimum|starting at|min(?:imum)?)\s*{_price}',
            text, re.I,
        )
        if m:
            filters["price_min"] = _parse_price_cents(m.group(1))

    # ── Mileage ─────────────────────────────────────────────────────────────

    m = re.search(
        r'\b(?:under|below|less than|max(?:imum)?|no more than)\s*([\d,]+k?)\s*(?:miles?|mi)\b',
        text, re.I,
    )
    if m:
        raw = m.group(1).replace(",", "")
        if raw.lower().endswith("k"):
            filters["mileage_max"] = round(float(raw[:-1]) * 1_000)
        else:
            filters["mileage_max"] = int(raw)

    # ── Condition ───────────────────────────────────────────────────────────

    if re.search(r'\b(?:certified|cpo|certified\s+pre[-\s]?owned)\b', text):
        filters["condition"] = "certified"
    elif re.search(r'\bsalvage\b', text):
        filters["condition"] = "salvage"

    # ── State ───────────────────────────────────────────────────────────────

    # Check full state names first (longest match wins), then abbreviations
    for name in sorted(_US_STATES, key=len, reverse=True):
        if re.search(rf'\b{re.escape(name)}\b', text):
            filters["state"] = _US_STATES[name]
            break

    # ── Make (longest match wins to handle "Land Rover" before "Rover") ─────

    for make in sorted(_COMMON_MAKES, key=len, reverse=True):
        if re.search(rf'\b{re.escape(make)}\b', text):
            filters["make"] = _MAKE_ALIASES.get(make, make.title())
            break

    # ── Remaining descriptive terms → query ─────────────────────────────────

    descriptors: list[str] = []
    for term in [*_COLORS, *_DRIVETRAINS, *_BODY_TYPES]:
        if re.search(rf'\b{re.escape(term)}\b', text):
            descriptors.append(term)
    if descriptors:
        filters["query"] = " ".join(sorted(set(descriptors)))

    # ── Explanation ─────────────────────────────────────────────────────────

    parts: list[str] = []
    if filters.get("make"):
        parts.append(filters["make"])
    if "year_min" in filters and "year_max" in filters:
        parts.append(f"{filters['year_min']}–{filters['year_max']}")
    elif "year_max" in filters:
        parts.append(f"built before {filters['year_max']}")
    elif "year_min" in filters:
        parts.append(f"built after {filters['year_min']}")
    if "price_min" in filters and "price_max" in filters:
        parts.append(f"${filters['price_min'] // 100:,}–${filters['price_max'] // 100:,}")
    elif "price_max" in filters:
        parts.append(f"under ${filters['price_max'] // 100:,}")
    elif "price_min" in filters:
        parts.append(f"over ${filters['price_min'] // 100:,}")
    if "mileage_max" in filters:
        parts.append(f"under {filters['mileage_max']:,} miles")
    if filters.get("condition"):
        parts.append(filters["condition"])
    if filters.get("state"):
        parts.append(f"in {filters['state']}")
    if descriptors:
        parts.extend(descriptors)

    explanation = (
        ", ".join(parts)
        if parts
        else "no specific filters detected — showing all listings"
    )
    return filters, explanation
