"""
Seed the database with realistic used car listings for development/demo.

Usage (from inside the backend container or with DB accessible):
    python seed.py
"""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

# Format: (Make, Model, Year, Trim, Price($), Mileage, Color, City, State, StockNum, Condition)
SEED_LISTINGS = [
    # ── Toyota (12) ──────────────────────────────────────────────────────────
    ("Toyota", "Camry",       2022, "SE",              26995,  18420, "Midnight Black",        "Los Angeles",   "CA", "SEED001", "used"),
    ("Toyota", "Camry",       2019, "XSE",             22500,  42100, "Midnight Black",        "Phoenix",       "AZ", "SEED002", "used"),
    ("Toyota", "Corolla",     2021, "LE",              19800,  28600, "Classic Silver",        "Chicago",       "IL", "SEED003", "used"),
    ("Toyota", "RAV4",        2023, "XLE",             32800,  12300, "Blueprint",             "Seattle",       "WA", "SEED004", "certified"),
    ("Toyota", "RAV4",        2020, "Adventure",       29500,  38900, "Magnetic Gray",         "Denver",        "CO", "SEED005", "used"),
    ("Toyota", "Highlander",  2023, "XLE",             47800,   7600, "Celestial Silver",      "Dallas",        "TX", "SEED006", "certified"),
    ("Toyota", "Tacoma",      2022, "TRD Pro",         52900,  18200, "Army Green",            "Portland",      "OR", "SEED007", "used"),
    ("Toyota", "Tacoma",      2019, "SR5",             34500,  51200, "Super White",           "Houston",       "TX", "SEED008", "used"),
    ("Toyota", "Tundra",      2023, "Platinum",        61500,   8900, "Wind Chill Pearl",      "Nashville",     "TN", "SEED009", "certified"),
    ("Toyota", "4Runner",     2022, "TRD Off-Road",    48500,  22000, "Magnetic Gray",         "Portland",      "OR", "SEED010", "used"),
    ("Toyota", "Prius",       2022, "XLE",             31200,  19800, "Reservoir Blue",        "San Francisco", "CA", "SEED011", "used"),
    ("Toyota", "Supra",       2023, "3.0",             55900,   6700, "Renaissance Red",       "Miami",         "FL", "SEED012", "used"),

    # ── Ford (12) ────────────────────────────────────────────────────────────
    ("Ford", "F-150",    2021, "XLT",             38900, 34200, "Velocity Blue",     "Dallas",        "TX", "SEED013", "used"),
    ("Ford", "F-150",    2023, "Lariat",          58900,  9100, "Star White",        "San Antonio",   "TX", "SEED014", "certified"),
    ("Ford", "F-150",    2019, "XL",              24500, 78900, "Oxford White",      "Oklahoma City", "OK", "SEED015", "used"),
    ("Ford", "Explorer", 2021, "XLT",             37900, 38500, "Star White",        "Atlanta",       "GA", "SEED016", "used"),
    ("Ford", "Explorer", 2023, "ST",              54200, 11800, "Carbonized Gray",   "Indianapolis",  "IN", "SEED017", "certified"),
    ("Ford", "Mustang",  2022, "GT",              42500, 15600, "Race Red",          "Houston",       "TX", "SEED018", "used"),
    ("Ford", "Mustang",  2020, "EcoBoost",        29800, 32400, "Grabber Blue",      "Columbus",      "OH", "SEED019", "used"),
    ("Ford", "Escape",   2022, "SEL",             29500, 21300, "Iconic Silver",     "Philadelphia",  "PA", "SEED020", "used"),
    ("Ford", "Ranger",   2022, "XLT",             33500, 19800, "Carbonized Gray",   "Denver",        "CO", "SEED021", "used"),
    ("Ford", "Bronco",   2022, "Outer Banks",     47900, 16700, "Area 51",           "Phoenix",       "AZ", "SEED022", "used"),
    ("Ford", "Bronco",   2023, "Raptor",          78500,  5400, "Hot Pepper Red",    "Las Vegas",     "NV", "SEED023", "used"),
    ("Ford", "Edge",     2021, "SEL",             28900, 33600, "Star White",        "Charlotte",     "NC", "SEED024", "used"),

    # ── Honda (9) ────────────────────────────────────────────────────────────
    ("Honda", "Civic",    2023, "Sport",       24500,  8900, "Sonic Gray Pearl",       "Chicago",       "IL", "SEED025", "used"),
    ("Honda", "Civic",    2020, "EX",          19800, 41200, "Lunar Silver Metallic",  "Boston",        "MA", "SEED026", "used"),
    ("Honda", "Accord",   2022, "Sport 2.0T", 33400, 21800, "Still Night Pearl",      "Phoenix",       "AZ", "SEED027", "used"),
    ("Honda", "Accord",   2019, "EX-L",       24500, 48900, "Champagne Frost Pearl",  "Minneapolis",   "MN", "SEED028", "used"),
    ("Honda", "CR-V",     2022, "EX-L",       34200, 19500, "Platinum White Pearl",   "Atlanta",       "GA", "SEED029", "used"),
    ("Honda", "CR-V",     2020, "Touring",    30500, 38200, "Sonic Gray Pearl",       "San Diego",     "CA", "SEED030", "used"),
    ("Honda", "Pilot",    2022, "EX-L",       42800, 22400, "Sonic Gray Pearl",       "Seattle",       "WA", "SEED031", "used"),
    ("Honda", "Odyssey",  2021, "EX-L",       38500, 31200, "Lunar Silver Metallic",  "Salt Lake City","UT", "SEED032", "used"),
    ("Honda", "Ridgeline",2022, "RTL-E",      46200, 18900, "Still Night Pearl",      "Denver",        "CO", "SEED033", "used"),

    # ── Chevrolet (7) ────────────────────────────────────────────────────────
    ("Chevrolet", "Silverado 1500", 2022, "LT",       41500, 27800, "Summit White",    "Phoenix",   "AZ", "SEED034", "used"),
    ("Chevrolet", "Silverado 1500", 2020, "LTZ",      44800, 49200, "Satin Steel",     "Kansas City","MO", "SEED035", "used"),
    ("Chevrolet", "Equinox",        2023, "LT",       31600,  5900, "Moonlight Gray",  "Miami",     "FL", "SEED036", "certified"),
    ("Chevrolet", "Traverse",       2022, "RS",       42900, 18700, "Midnight Blue",   "Detroit",   "MI", "SEED037", "used"),
    ("Chevrolet", "Camaro",         2022, "SS",       49800, 14300, "Rally Green",     "Chicago",   "IL", "SEED038", "used"),
    ("Chevrolet", "Colorado",       2022, "Z71",      38400, 22100, "Rally Green",     "Denver",    "CO", "SEED039", "used"),
    ("Chevrolet", "Tahoe",          2022, "Z71",      62500, 19800, "Midnight Blue",   "Dallas",    "TX", "SEED040", "used"),

    # ── BMW (7) ──────────────────────────────────────────────────────────────
    ("BMW", "3 Series", 2022, "330i",        43900, 22100, "Alpine White",    "New York",      "NY", "SEED041", "used"),
    ("BMW", "3 Series", 2020, "M340i",       48500, 38900, "Portimao Blue",   "Los Angeles",   "CA", "SEED042", "used"),
    ("BMW", "5 Series", 2022, "530i",        56900, 17400, "Black Sapphire",  "San Francisco", "CA", "SEED043", "used"),
    ("BMW", "X3",       2022, "xDrive30i",   49800, 21200, "Mineral White",   "Chicago",       "IL", "SEED044", "certified"),
    ("BMW", "X5",       2021, "xDrive40i",   64900, 28700, "Carbon Black",    "Miami",         "FL", "SEED045", "used"),
    ("BMW", "M3",       2023, "Competition", 85900,  6200, "Isle of Man Green","Los Angeles",  "CA", "SEED046", "used"),
    ("BMW", "4 Series", 2022, "430i Coupe",  52400, 19800, "Brooklyn Grey",   "Boston",        "MA", "SEED047", "used"),

    # ── Mercedes-Benz (7) ────────────────────────────────────────────────────
    ("Mercedes-Benz", "C-Class", 2021, "C300",      39500, 29800, "Obsidian Black",  "Los Angeles",   "CA", "SEED048", "used"),
    ("Mercedes-Benz", "C-Class", 2023, "AMG C43",   68900,  5800, "Spectral Blue",   "Miami",         "FL", "SEED049", "used"),
    ("Mercedes-Benz", "E-Class", 2022, "E350",      58900, 18400, "Selenite Grey",   "New York",      "NY", "SEED050", "used"),
    ("Mercedes-Benz", "GLE",     2022, "GLE350",    67800, 21200, "Obsidian Black",  "Dallas",        "TX", "SEED051", "certified"),
    ("Mercedes-Benz", "GLC",     2023, "GLC300",    54900,  9800, "Digital White",   "Seattle",       "WA", "SEED052", "certified"),
    ("Mercedes-Benz", "S-Class", 2021, "S500",      98900, 22100, "Obsidian Black",  "Beverly Hills", "CA", "SEED053", "used"),
    ("Mercedes-Benz", "GLA",     2023, "GLA250",    42900, 12800, "Polar White",     "Boston",        "MA", "SEED054", "certified"),

    # ── Jeep (8) ─────────────────────────────────────────────────────────────
    ("Jeep", "Grand Cherokee", 2021, "Laredo",    36750, 41200, "Diamond Black",      "Miami",         "FL", "SEED055", "used"),
    ("Jeep", "Grand Cherokee", 2023, "Overland",  58900,  8900, "Bright White",       "Denver",        "CO", "SEED056", "certified"),
    ("Jeep", "Wrangler",       2022, "Rubicon",   52400, 19800, "Sarge Green",        "Phoenix",       "AZ", "SEED057", "used"),
    ("Jeep", "Wrangler",       2020, "Sport S",   36900, 42100, "Firecracker Red",    "Albuquerque",   "NM", "SEED058", "used"),
    ("Jeep", "Cherokee",       2021, "Trailhawk", 32800, 33600, "Granite Crystal",    "Charlotte",     "NC", "SEED059", "used"),
    ("Jeep", "Compass",        2022, "Latitude",  27500, 22400, "Slate Blue Pearl",   "Indianapolis",  "IN", "SEED060", "used"),
    ("Jeep", "Gladiator",      2022, "Mojave",    54900, 14200, "Hydro Blue Pearl",   "Salt Lake City","UT", "SEED061", "used"),
    ("Jeep", "Gladiator",      2023, "Rubicon",   62500,  7800, "Sting-Gray",         "Austin",        "TX", "SEED062", "certified"),

    # ── Tesla (6) ────────────────────────────────────────────────────────────
    ("Tesla", "Model 3", 2023, "Long Range",          44990,  9800, "Pearl White",        "San Francisco", "CA", "SEED063", "used"),
    ("Tesla", "Model 3", 2021, "Standard Range Plus", 34500, 28900, "Midnight Silver",    "Seattle",       "WA", "SEED064", "used"),
    ("Tesla", "Model Y", 2023, "Performance",         56990,  8200, "Red Multi-Coat",     "Los Angeles",   "CA", "SEED065", "used"),
    ("Tesla", "Model Y", 2022, "Long Range",          52500, 18400, "Pearl White",        "Austin",        "TX", "SEED066", "used"),
    ("Tesla", "Model S", 2022, "Plaid",              119990, 12300, "Midnight Silver",    "Beverly Hills", "CA", "SEED067", "used"),
    ("Tesla", "Model X", 2022, "Long Range",         108990, 15600, "Pearl White",        "San Jose",      "CA", "SEED068", "used"),

    # ── Subaru (6) ───────────────────────────────────────────────────────────
    ("Subaru", "Outback",  2022, "Premium",  29900, 23400, "Autumn Green",      "Portland",    "OR", "SEED069", "used"),
    ("Subaru", "Forester", 2022, "Sport",    32500, 19800, "Magnetite Gray",    "Seattle",     "WA", "SEED070", "used"),
    ("Subaru", "Crosstrek",2023, "Limited",  29800,  8900, "Cool Gray Khaki",   "Denver",      "CO", "SEED071", "certified"),
    ("Subaru", "WRX",      2023, "Premium",  34900,  9200, "WR Blue Pearl",     "Chicago",     "IL", "SEED072", "used"),
    ("Subaru", "Ascent",   2022, "Touring",  45800, 18700, "Brilliant Silver",  "Minneapolis", "MN", "SEED073", "used"),
    ("Subaru", "Impreza",  2022, "Sport",    24500, 21400, "Pure Red",          "Boston",      "MA", "SEED074", "used"),

    # ── Nissan (6) ───────────────────────────────────────────────────────────
    ("Nissan", "Altima",    2022, "SV",      25800, 24600, "Midnight Black",           "New York",  "NY", "SEED075", "used"),
    ("Nissan", "Rogue",     2023, "SL",      34900, 11200, "Everlasting Silver",       "Atlanta",   "GA", "SEED076", "certified"),
    ("Nissan", "Pathfinder",2022, "SL",      42800, 18900, "Magnetic Black Pearl",     "Dallas",    "TX", "SEED077", "used"),
    ("Nissan", "Frontier",  2022, "Pro-4X",  38500, 22100, "Gun Metallic",             "Phoenix",   "AZ", "SEED078", "used"),
    ("Nissan", "Murano",    2022, "SL",      38900, 19400, "Cashmere",                 "Chicago",   "IL", "SEED079", "used"),
    ("Nissan", "370Z",      2020, "Sport",   32800, 28400, "Magnetic Black Pearl",     "Miami",     "FL", "SEED080", "used"),

    # ── Hyundai (6) ──────────────────────────────────────────────────────────
    ("Hyundai", "Tucson",   2022, "SEL Convenience", 30500, 17200, "Amazon Gray",          "Denver",    "CO", "SEED081", "used"),
    ("Hyundai", "Santa Fe", 2022, "SEL",             36200, 21800, "Calypso Red Pearl",    "Charlotte", "NC", "SEED082", "used"),
    ("Hyundai", "Elantra",  2023, "N Line",          25800,  9400, "Performance Blue",     "Austin",    "TX", "SEED083", "used"),
    ("Hyundai", "Sonata",   2022, "SEL Plus",        30900, 18600, "Shimmering Silver",    "Nashville", "TN", "SEED084", "used"),
    ("Hyundai", "Palisade", 2022, "Calligraphy",     51200, 16800, "Moonlight Cloud",      "Seattle",   "WA", "SEED085", "used"),
    ("Hyundai", "Ioniq 6",  2023, "SE Long Range",   42800,  7200, "Gravity Gold Matte",   "Los Angeles","CA","SEED086", "used"),

    # ── Kia (6) ──────────────────────────────────────────────────────────────
    ("Kia", "Sportage",  2023, "EX",           31200, 11400, "Snow White Pearl",      "Nashville",    "TN", "SEED087", "certified"),
    ("Kia", "Sorento",   2022, "SX Prestige",  45800, 18900, "Midnight Black Pearl",  "Philadelphia", "PA", "SEED088", "used"),
    ("Kia", "Telluride", 2023, "SX-P",         52900,  9800, "Everlasting Silver",    "Dallas",       "TX", "SEED089", "used"),
    ("Kia", "EV6",       2023, "Wind AWD",     49800,  8200, "Runway Red",            "San Francisco","CA", "SEED090", "used"),
    ("Kia", "Stinger",   2022, "GT2",          44900, 21200, "Aurora Black Pearl",    "Miami",        "FL", "SEED091", "used"),
    ("Kia", "Carnival",  2022, "SX Prestige",  48200, 16400, "Ebony Black",           "Chicago",      "IL", "SEED092", "used"),

    # ── Dodge / Ram (6) ──────────────────────────────────────────────────────
    ("Dodge", "Challenger", 2021, "R/T",        38200, 31900, "Frostbite Blue",          "Las Vegas",  "NV", "SEED093", "used"),
    ("Dodge", "Challenger", 2023, "Hellcat",    78900,  6200, "Frostbite Blue",          "Los Angeles","CA", "SEED094", "used"),
    ("Dodge", "Charger",    2022, "Scat Pack",  52800, 18400, "Triple Nickel",           "Houston",    "TX", "SEED095", "used"),
    ("Ram",   "1500",       2023, "Big Horn",   45900,  8100, "Bright White",            "Nashville",  "TN", "SEED096", "certified"),
    ("Ram",   "1500",       2020, "Tradesman",  34500, 58400, "Granite Crystal",         "Oklahoma City","OK","SEED097","used"),
    ("Ram",   "2500",       2022, "Laramie",    62800, 22900, "Diamond Black Crystal",   "Denver",     "CO", "SEED098", "used"),

    # ── GMC (5) ──────────────────────────────────────────────────────────────
    ("GMC", "Sierra 1500", 2022, "SLE",     43200, 29100, "Onyx Black",        "Houston",     "TX", "SEED099", "used"),
    ("GMC", "Sierra 1500", 2023, "Denali",  67500,  9800, "Dark Sky Metallic", "Dallas",      "TX", "SEED100", "certified"),
    ("GMC", "Yukon",       2022, "SLT",     68900, 22400, "Satin Steel",       "Chicago",     "IL", "SEED101", "used"),
    ("GMC", "Canyon",      2022, "AT4",     42800, 18900, "Satin Steel",       "Denver",      "CO", "SEED102", "used"),
    ("GMC", "Acadia",      2022, "AT4",     43500, 21200, "Ebony Twilight",    "Minneapolis", "MN", "SEED103", "used"),

    # ── Audi (5) ─────────────────────────────────────────────────────────────
    ("Audi", "A4",    2022, "Premium Plus", 46500, 18700, "Myth Black",      "Chicago",       "IL", "SEED104", "used"),
    ("Audi", "Q5",    2022, "Premium Plus", 52900, 19800, "Florett Silver",  "Boston",        "MA", "SEED105", "certified"),
    ("Audi", "Q7",    2021, "Premium Plus", 63400, 28900, "Glacier White",   "New York",      "NY", "SEED106", "used"),
    ("Audi", "A6",    2022, "Premium Plus", 58900, 22400, "District Green",  "Los Angeles",   "CA", "SEED107", "used"),
    ("Audi", "e-tron",2022, "Premium Plus", 68900, 18400, "Chronos Grey",    "San Francisco", "CA", "SEED108", "used"),

    # ── Lexus (5) ────────────────────────────────────────────────────────────
    ("Lexus", "RX 350",  2022, "Luxury",     52900, 14200, "Atomic Silver",       "Seattle",   "WA", "SEED109", "used"),
    ("Lexus", "IS 350",  2022, "F SPORT",    46800, 18900, "Obsidian",            "Los Angeles","CA", "SEED110", "used"),
    ("Lexus", "GX 460",  2022, "Premium",    59800, 21200, "Nightfall Mica",      "Dallas",    "TX", "SEED111", "used"),
    ("Lexus", "NX 350",  2023, "F SPORT",    48900,  9800, "Eminent White Pearl", "Chicago",   "IL", "SEED112", "certified"),
    ("Lexus", "LC 500",  2022, "Coupe",      99800,  8400, "Structural Blue",     "Miami",     "FL", "SEED113", "used"),

    # ── Porsche (5) ──────────────────────────────────────────────────────────
    ("Porsche", "Cayenne",  2022, "Base",     79800, 18400, "Jet Black Metallic",    "Los Angeles",   "CA", "SEED114", "used"),
    ("Porsche", "Macan",    2022, "S",        62400, 21800, "Gentian Blue",          "San Francisco", "CA", "SEED115", "used"),
    ("Porsche", "911",      2022, "Carrera 4S",128900,8900, "Guards Red",            "Miami",         "FL", "SEED116", "used"),
    ("Porsche", "Taycan",   2023, "4S",      109900,  7200, "Frozen Blue Metallic",  "Beverly Hills", "CA", "SEED117", "used"),
    ("Porsche", "Panamera", 2021, "4 E-Hybrid",94500,22100, "Night Blue Metallic",   "New York",      "NY", "SEED118", "used"),

    # ── Volkswagen (4) ───────────────────────────────────────────────────────
    ("Volkswagen", "Jetta",   2023, "SEL",              27450,  6700, "Platinum Gray",     "Boston",  "MA", "SEED119", "used"),
    ("Volkswagen", "Tiguan",  2022, "SEL Premium",      39800, 18400, "Deep Black Pearl",  "Chicago", "IL", "SEED120", "used"),
    ("Volkswagen", "ID.4",    2023, "Pro",              41800,  9200, "Coastal Blue",      "Portland","OR", "SEED121", "used"),
    ("Volkswagen", "Golf GTI",2022, "Autobahn",         38900, 14200, "Tornado Red",       "Denver",  "CO", "SEED122", "used"),

    # ── Mazda (4) ────────────────────────────────────────────────────────────
    ("Mazda", "CX-5",     2023, "Grand Touring", 36200,  8300, "Soul Red Crystal",  "Los Angeles","CA", "SEED123", "used"),
    ("Mazda", "CX-9",     2022, "Signature",     47800, 18900, "Machine Gray",      "Seattle",   "WA", "SEED124", "used"),
    ("Mazda", "Mazda3",   2022, "Premium Plus",  28900, 21400, "Polymetal Gray",    "Portland",  "OR", "SEED125", "used"),
    ("Mazda", "MX-5 Miata",2023,"RF Grand Touring",39800,7800,"Soul Red Crystal",  "San Diego", "CA", "SEED126", "used"),

    # ── Volvo (4) ────────────────────────────────────────────────────────────
    ("Volvo", "XC60", 2022, "T6 Momentum",   48900, 16400, "Crystal White Pearl",  "Boston",      "MA", "SEED127", "certified"),
    ("Volvo", "XC90", 2022, "T6 Inscription",62800, 19800, "Crystal White Pearl",  "Seattle",     "WA", "SEED128", "certified"),
    ("Volvo", "S60",  2022, "T5 Momentum",   38900, 22400, "Denim Blue",           "Chicago",     "IL", "SEED129", "used"),
    ("Volvo", "V60",  2022, "T5 Inscription",41800, 18200, "Pebble Grey",          "Minneapolis", "MN", "SEED130", "used"),

    # ── Cadillac (4) ─────────────────────────────────────────────────────────
    ("Cadillac", "Escalade", 2021, "Premium Luxury",   87500, 28400, "Black Raven",       "Las Vegas",  "NV", "SEED131", "used"),
    ("Cadillac", "XT5",      2022, "Premium Luxury",   49800, 19200, "Radiant Silver",    "Dallas",     "TX", "SEED132", "used"),
    ("Cadillac", "CT5",      2022, "V-Series Blackwing",89900,12400, "Emerald Lake Blue", "Chicago",    "IL", "SEED133", "used"),
    ("Cadillac", "XT4",      2022, "Premium Luxury",   42800, 21900, "Radiant Silver",    "Atlanta",    "GA", "SEED134", "used"),

    # ── Budget / older (16) — price diversity ─────────────────────────────────
    ("Honda",      "Civic",      2015, "LX",       9500, 98400, "Crystal Black Pearl",  "Cleveland",    "OH", "SEED135", "used"),
    ("Toyota",     "Corolla",    2016, "LE",       10800, 87200, "Classic Silver",       "Pittsburgh",   "PA", "SEED136", "used"),
    ("Ford",       "Focus",      2017, "SE",        9200, 91800, "Magnetic",             "Memphis",      "TN", "SEED137", "used"),
    ("Chevrolet",  "Malibu",     2018, "LT",       14800, 62400, "Summit White",         "Louisville",   "KY", "SEED138", "used"),
    ("Nissan",     "Sentra",     2019, "SV",       13900, 54200, "Deep Blue Pearl",      "Richmond",     "VA", "SEED139", "used"),
    ("Hyundai",    "Elantra",    2018, "SE",       11500, 72400, "Scarlet Red Pearl",    "Raleigh",      "NC", "SEED140", "used"),
    ("Kia",        "Soul",       2019, "LX",       13200, 58900, "Shadow Black",         "Columbia",     "SC", "SEED141", "used"),
    ("Mazda",      "Mazda6",     2018, "Sport",    14800, 68400, "Machine Gray",         "Tucson",       "AZ", "SEED142", "used"),
    ("Subaru",     "Impreza",    2016, "2.0i",     12400, 82400, "Ice Silver",           "Burlington",   "VT", "SEED143", "used"),
    ("Volkswagen", "Jetta",      2017, "SE",       10900, 79800, "Pure White",           "Boise",        "ID", "SEED144", "used"),
    ("Ford",       "Fusion",     2018, "SE",       12800, 68200, "Oxford White",         "Omaha",        "NE", "SEED145", "used"),
    ("Honda",      "HR-V",       2019, "LX",       16800, 52400, "Lunar Silver Metallic","Albuquerque",  "NM", "SEED146", "used"),
    ("Toyota",     "Yaris",      2019, "LE",       13400, 61200, "Absolutely Red",       "El Paso",      "TX", "SEED147", "used"),
    ("Chevrolet",  "Spark",      2020, "LS",        9800, 44200, "Red Hot",              "Tulsa",        "OK", "SEED148", "used"),
    ("Mitsubishi", "Outlander",  2020, "SE",       21500, 38400, "Diamond White",        "Wichita",      "KS", "SEED149", "used"),
    ("Acura",      "TLX",        2021, "Technology",38900,24200, "Majestic Black Pearl", "Jacksonville", "FL", "SEED150", "used"),
]

PHOTO_URLS: dict[tuple, str] = {
    ("Toyota",     "Camry"):        "https://media.ed.edmunds-media.com/toyota/camry/2022/oem/2022_toyota_camry_sedan_se_fq_oem_1_1600.jpg",
    ("Toyota",     "RAV4"):         "https://media.ed.edmunds-media.com/toyota/rav4/2023/oem/2023_toyota_rav4_4door-suv_xle_fq_oem_1_1600.jpg",
    ("Toyota",     "Highlander"):   "https://media.ed.edmunds-media.com/toyota/highlander/2023/oem/2023_toyota_highlander_4door-suv_xle_fq_oem_1_1600.jpg",
    ("Toyota",     "Tacoma"):       "https://media.ed.edmunds-media.com/toyota/tacoma/2022/oem/2022_toyota_tacoma_truck_trd-pro_fq_oem_1_1600.jpg",
    ("Toyota",     "4Runner"):      "https://media.ed.edmunds-media.com/toyota/4runner/2022/oem/2022_toyota_4runner_4door-suv_trd-off-road_fq_oem_1_1600.jpg",
    ("Toyota",     "Corolla"):      "https://media.ed.edmunds-media.com/toyota/corolla/2021/oem/2021_toyota_corolla_sedan_le_fq_oem_1_1600.jpg",
    ("Toyota",     "Supra"):        "https://media.ed.edmunds-media.com/toyota/gr-supra/2023/oem/2023_toyota_gr-supra_coupe_30_fq_oem_1_1600.jpg",
    ("Ford",       "F-150"):        "https://media.ed.edmunds-media.com/ford/f-150/2021/oem/2021_ford_f-150_truck_xlt_fq_oem_1_1600.jpg",
    ("Ford",       "Explorer"):     "https://media.ed.edmunds-media.com/ford/explorer/2021/oem/2021_ford_explorer_4door-suv_xlt_fq_oem_1_1600.jpg",
    ("Ford",       "Mustang"):      "https://media.ed.edmunds-media.com/ford/mustang/2022/oem/2022_ford_mustang_coupe_gt_fq_oem_1_1600.jpg",
    ("Ford",       "Bronco"):       "https://media.ed.edmunds-media.com/ford/bronco/2022/oem/2022_ford_bronco_4door-suv_outer-banks_fq_oem_1_1600.jpg",
    ("Honda",      "Civic"):        "https://media.ed.edmunds-media.com/honda/civic/2023/oem/2023_honda_civic_sedan_sport_fq_oem_1_1600.jpg",
    ("Honda",      "CR-V"):         "https://media.ed.edmunds-media.com/honda/cr-v/2022/oem/2022_honda_cr-v_4door-suv_ex-l_fq_oem_1_1600.jpg",
    ("Honda",      "Accord"):       "https://media.ed.edmunds-media.com/honda/accord/2022/oem/2022_honda_accord_sedan_sport-20t_fq_oem_1_1600.jpg",
    ("Chevrolet",  "Silverado 1500"):"https://media.ed.edmunds-media.com/chevrolet/silverado-1500/2022/oem/2022_chevrolet_silverado-1500_truck_lt_fq_oem_1_1600.jpg",
    ("Chevrolet",  "Camaro"):       "https://media.ed.edmunds-media.com/chevrolet/camaro/2022/oem/2022_chevrolet_camaro_coupe_ss_fq_oem_1_1600.jpg",
    ("BMW",        "3 Series"):     "https://media.ed.edmunds-media.com/bmw/3-series/2022/oem/2022_bmw_3-series_sedan_330i_fq_oem_1_1600.jpg",
    ("BMW",        "X5"):           "https://media.ed.edmunds-media.com/bmw/x5/2021/oem/2021_bmw_x5_4door-suv_xdrive40i_fq_oem_1_1600.jpg",
    ("Jeep",       "Wrangler"):     "https://media.ed.edmunds-media.com/jeep/wrangler/2022/oem/2022_jeep_wrangler_convertible_rubicon_fq_oem_1_1600.jpg",
    ("Jeep",       "Grand Cherokee"):"https://media.ed.edmunds-media.com/jeep/grand-cherokee/2021/oem/2021_jeep_grand-cherokee_4door-suv_laredo_fq_oem_1_1600.jpg",
    ("Jeep",       "Gladiator"):    "https://media.ed.edmunds-media.com/jeep/gladiator/2022/oem/2022_jeep_gladiator_truck_mojave_fq_oem_1_1600.jpg",
    ("Tesla",      "Model 3"):      "https://media.ed.edmunds-media.com/tesla/model-3/2023/oem/2023_tesla_model-3_sedan_long-range_fq_oem_1_1600.jpg",
    ("Tesla",      "Model Y"):      "https://media.ed.edmunds-media.com/tesla/model-y/2022/oem/2022_tesla_model-y_4door-suv_performance_fq_oem_1_1600.jpg",
    ("Subaru",     "Outback"):      "https://media.ed.edmunds-media.com/subaru/outback/2022/oem/2022_subaru_outback_4door-suv_premium_fq_oem_1_1600.jpg",
    ("Ram",        "1500"):         "https://media.ed.edmunds-media.com/ram/1500/2023/oem/2023_ram_1500_truck_big-horn_fq_oem_1_1600.jpg",
    ("Mazda",      "CX-5"):         "https://media.ed.edmunds-media.com/mazda/cx-5/2023/oem/2023_mazda_cx-5_4door-suv_grand-touring_fq_oem_1_1600.jpg",
    ("Lexus",      "RX 350"):       "https://media.ed.edmunds-media.com/lexus/rx/2022/oem/2022_lexus_rx_4door-suv_rx-350-luxury_fq_oem_1_1600.jpg",
    ("Cadillac",   "Escalade"):     "https://media.ed.edmunds-media.com/cadillac/escalade/2021/oem/2021_cadillac_escalade_4door-suv_premium-luxury_fq_oem_1_1600.jpg",
    ("Porsche",    "911"):          "https://media.ed.edmunds-media.com/porsche/911/2022/oem/2022_porsche_911_coupe_carrera-4s_fq_oem_1_1600.jpg",
    ("Audi",       "Q5"):           "https://media.ed.edmunds-media.com/audi/q5/2022/oem/2022_audi_q5_4door-suv_premium-plus_fq_oem_1_1600.jpg",
    ("Dodge",      "Challenger"):   "https://media.ed.edmunds-media.com/dodge/challenger/2021/oem/2021_dodge_challenger_coupe_rt_fq_oem_1_1600.jpg",
    ("GMC",        "Sierra 1500"):  "https://media.ed.edmunds-media.com/gmc/sierra-1500/2022/oem/2022_gmc_sierra-1500_truck_sle_fq_oem_1_1600.jpg",
    ("Hyundai",    "Tucson"):       "https://media.ed.edmunds-media.com/hyundai/tucson/2022/oem/2022_hyundai_tucson_4door-suv_sel_fq_oem_1_1600.jpg",
    ("Kia",        "Telluride"):    "https://media.ed.edmunds-media.com/kia/telluride/2023/oem/2023_kia_telluride_4door-suv_sx_fq_oem_1_1600.jpg",
    ("Volvo",      "XC60"):         "https://media.ed.edmunds-media.com/volvo/xc60/2022/oem/2022_volvo_xc60_4door-suv_t6-momentum_fq_oem_1_1600.jpg",
}

FALLBACK_PHOTOS = [
    "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80",
    "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800&q=80",
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&q=80",
    "https://images.unsplash.com/photo-1542362567-b07e54358753?w=800&q=80",
]


async def main() -> None:
    async with Session() as db:
        from sqlalchemy import text as sql_text
        row = (await db.execute(sql_text("SELECT id FROM sources WHERE name = 'carmax' LIMIT 1"))).fetchone()
        if not row:
            print("ERROR: 'carmax' source not found. Run migrations first.")
            return
        source_id = row[0]
        print(f"Using source_id={source_id} — seeding {len(SEED_LISTINGS)} listings...")

        count = 0
        for entry in SEED_LISTINGS:
            (make, model, year, trim, price_usd, mileage, color, city, state, stock, condition) = entry
            listing_id = uuid.uuid4()
            price_cents = price_usd * 100
            title = f"{year} {make} {model} {trim}"
            photo_url = PHOTO_URLS.get((make, model), FALLBACK_PHOTOS[count % len(FALLBACK_PHOTOS)])

            await db.execute(sql_text("""
                INSERT INTO listings
                    (id, source_id, external_id, url, title, price, mileage, year, make, model, trim,
                     color_exterior, condition, location_city, location_state, dealer_name,
                     is_active, first_seen_at, last_seen_at)
                VALUES
                    (:id, :source_id, :external_id, :url, :title, :price, :mileage, :year,
                     :make, :model, :trim, :color_exterior, :condition, :location_city,
                     :location_state, :dealer_name, true, NOW(), NOW())
                ON CONFLICT (source_id, external_id) DO UPDATE SET
                    price = EXCLUDED.price,
                    condition = EXCLUDED.condition,
                    last_seen_at = NOW()
                RETURNING id
            """), {
                "id": str(listing_id),
                "source_id": source_id,
                "external_id": stock,
                "url": f"https://www.carmax.com/car/{stock}",
                "title": title,
                "price": price_cents,
                "mileage": mileage,
                "year": year,
                "make": make,
                "model": model,
                "trim": trim,
                "color_exterior": color,
                "condition": condition,
                "location_city": city,
                "location_state": state,
                "dealer_name": "CarMax",
            })

            result2 = await db.execute(sql_text(
                "SELECT id FROM listings WHERE source_id = :sid AND external_id = :eid"
            ), {"sid": source_id, "eid": stock})
            actual_id = result2.scalar()

            await db.execute(sql_text("""
                INSERT INTO photos (id, listing_id, url, is_primary, sort_order)
                VALUES (:id, :listing_id, :url, true, 0)
                ON CONFLICT DO NOTHING
            """), {"id": str(uuid.uuid4()), "listing_id": str(actual_id), "url": photo_url})

            await db.execute(sql_text("""
                INSERT INTO price_history (listing_id, price, recorded_at)
                VALUES (:listing_id, :price, NOW())
            """), {"listing_id": str(actual_id), "price": price_cents})

            count += 1

        await db.commit()
        print(f"Seeded {count} listings successfully.")


if __name__ == "__main__":
    asyncio.run(main())
