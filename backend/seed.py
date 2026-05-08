"""
Seed the database with realistic used car listings for development/demo.

Usage (from inside the backend container or with DB accessible):
    python seed.py
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

SEED_LISTINGS = [
    # Make, Model, Year, Trim, Price($), Mileage, Color, City, State, StockNum
    ("Toyota", "Camry", 2022, "SE", 26995, 18420, "Midnight Black", "Los Angeles", "CA", "CM2022001"),
    ("Honda", "Civic", 2023, "Sport", 24500, 8900, "Sonic Gray Pearl", "Chicago", "IL", "HV2023001"),
    ("Ford", "F-150", 2021, "XLT", 38900, 34200, "Velocity Blue", "Dallas", "TX", "FF2021001"),
    ("Chevrolet", "Silverado 1500", 2022, "LT", 41500, 27800, "Summit White", "Phoenix", "AZ", "CS2022001"),
    ("Toyota", "RAV4", 2023, "XLE", 32800, 12300, "Blueprint", "Seattle", "WA", "TR2023001"),
    ("Honda", "CR-V", 2022, "EX-L", 34200, 19500, "Platinum White Pearl", "Atlanta", "GA", "HC2022001"),
    ("Jeep", "Grand Cherokee", 2021, "Laredo", 36750, 41200, "Diamond Black", "Miami", "FL", "JG2021001"),
    ("BMW", "3 Series", 2022, "330i", 43900, 22100, "Alpine White", "New York", "NY", "BM2022001"),
    ("Mercedes-Benz", "C-Class", 2021, "C300", 39500, 29800, "Obsidian Black", "Los Angeles", "CA", "MB2021001"),
    ("Tesla", "Model 3", 2023, "Long Range", 44990, 9800, "Pearl White", "San Francisco", "CA", "TE2023001"),
    ("Ford", "Mustang", 2022, "GT", 42500, 15600, "Race Red", "Houston", "TX", "FM2022001"),
    ("Subaru", "Outback", 2022, "Premium", 29900, 23400, "Autumn Green", "Portland", "OR", "SO2022001"),
    ("Volkswagen", "Jetta", 2023, "SEL", 27450, 6700, "Platinum Gray", "Boston", "MA", "VJ2023001"),
    ("Hyundai", "Tucson", 2022, "SEL Convenience", 30500, 17200, "Amazon Gray", "Denver", "CO", "HT2022001"),
    ("Kia", "Sportage", 2023, "EX", 31200, 11400, "Snow White Pearl", "Nashville", "TN", "KS2023001"),
    ("Dodge", "Challenger", 2021, "R/T", 38200, 31900, "Frostbite Blue", "Las Vegas", "NV", "DC2021001"),
    ("Audi", "A4", 2022, "Premium Plus", 46500, 18700, "Myth Black", "Chicago", "IL", "AA2022001"),
    ("Lexus", "RX 350", 2022, "Luxury", 52900, 14200, "Atomic Silver", "Seattle", "WA", "LR2022001"),
    ("Toyota", "Highlander", 2023, "XLE", 47800, 7600, "Celestial Silver", "Dallas", "TX", "TH2023001"),
    ("Honda", "Accord", 2022, "Sport 2.0T", 33400, 21800, "Still Night Pearl", "Phoenix", "AZ", "HA2022001"),
    ("Ford", "Explorer", 2021, "XLT", 37900, 38500, "Star White", "Atlanta", "GA", "FE2021001"),
    ("Chevrolet", "Equinox", 2023, "LT", 31600, 5900, "Moonlight Gray", "Miami", "FL", "CE2023001"),
    ("Nissan", "Altima", 2022, "SV", 25800, 24600, "Midnight Black", "New York", "NY", "NA2022001"),
    ("Mazda", "CX-5", 2023, "Grand Touring", 36200, 8300, "Soul Red Crystal", "Los Angeles", "CA", "MC2023001"),
    ("Volvo", "XC60", 2022, "T6 Momentum", 48900, 16400, "Crystal White Pearl", "Boston", "MA", "VC2022001"),
    ("GMC", "Sierra 1500", 2022, "SLE", 43200, 29100, "Onyx Black", "Houston", "TX", "GS2022001"),
    ("Chrysler", "Pacifica", 2021, "Touring L", 34500, 35700, "Brilliant Black", "Denver", "CO", "CP2021001"),
    ("Toyota", "4Runner", 2022, "TRD Off-Road", 48500, 22000, "Magnetic Gray", "Portland", "OR", "T4R2022001"),
    ("Ram", "1500", 2023, "Big Horn", 45900, 8100, "Bright White", "Nashville", "TN", "R152023001"),
    ("Cadillac", "Escalade", 2021, "Premium Luxury", 87500, 28400, "Black Raven", "Las Vegas", "NV", "CA2021001"),
]

PHOTO_URLS = {
    ("Toyota", "Camry"): "https://media.ed.edmunds-media.com/toyota/camry/2022/oem/2022_toyota_camry_sedan_se_fq_oem_1_1600.jpg",
    ("Honda", "Civic"): "https://media.ed.edmunds-media.com/honda/civic/2023/oem/2023_honda_civic_sedan_sport_fq_oem_1_1600.jpg",
    ("Ford", "F-150"): "https://media.ed.edmunds-media.com/ford/f-150/2021/oem/2021_ford_f-150_truck_xlt_fq_oem_1_1600.jpg",
    ("Chevrolet", "Silverado 1500"): "https://media.ed.edmunds-media.com/chevrolet/silverado-1500/2022/oem/2022_chevrolet_silverado-1500_truck_lt_fq_oem_1_1600.jpg",
    ("Toyota", "RAV4"): "https://media.ed.edmunds-media.com/toyota/rav4/2023/oem/2023_toyota_rav4_4door-suv_xle_fq_oem_1_1600.jpg",
    ("Honda", "CR-V"): "https://media.ed.edmunds-media.com/honda/cr-v/2022/oem/2022_honda_cr-v_4door-suv_ex-l_fq_oem_1_1600.jpg",
    ("BMW", "3 Series"): "https://media.ed.edmunds-media.com/bmw/3-series/2022/oem/2022_bmw_3-series_sedan_330i_fq_oem_1_1600.jpg",
    ("Tesla", "Model 3"): "https://media.ed.edmunds-media.com/tesla/model-3/2023/oem/2023_tesla_model-3_sedan_long-range_fq_oem_1_1600.jpg",
    ("Ford", "Mustang"): "https://media.ed.edmunds-media.com/ford/mustang/2022/oem/2022_ford_mustang_coupe_gt_fq_oem_1_1600.jpg",
    ("Toyota", "Highlander"): "https://media.ed.edmunds-media.com/toyota/highlander/2023/oem/2023_toyota_highlander_4door-suv_xle_fq_oem_1_1600.jpg",
    ("Honda", "Accord"): "https://media.ed.edmunds-media.com/honda/accord/2022/oem/2022_honda_accord_sedan_sport-20t_fq_oem_1_1600.jpg",
    ("Toyota", "4Runner"): "https://media.ed.edmunds-media.com/toyota/4runner/2022/oem/2022_toyota_4runner_4door-suv_trd-off-road_fq_oem_1_1600.jpg",
    ("Mazda", "CX-5"): "https://media.ed.edmunds-media.com/mazda/cx-5/2023/oem/2023_mazda_cx-5_4door-suv_grand-touring_fq_oem_1_1600.jpg",
    ("Lexus", "RX 350"): "https://media.ed.edmunds-media.com/lexus/rx/2022/oem/2022_lexus_rx_4door-suv_rx-350-luxury_fq_oem_1_1600.jpg",
    ("Ram", "1500"): "https://media.ed.edmunds-media.com/ram/1500/2023/oem/2023_ram_1500_truck_big-horn_fq_oem_1_1600.jpg",
}

FALLBACK_PHOTO = "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800&q=80"


async def main() -> None:
    async with Session() as db:
        # Get source ID for carmax
        result = await db.execute(select(text("id")).select_from(text("sources")).where(text("name = 'carmax'")))
        row = result.fetchone()
        if not row:
            print("ERROR: 'carmax' source row not found. Run migrations first.")
            return
        source_id = row[0]
        print(f"Using source_id={source_id}")

        count = 0
        for (make, model, year, trim, price_usd, mileage, color, city, state, stock) in SEED_LISTINGS:
            listing_id = uuid.uuid4()
            price_cents = price_usd * 100
            title = f"{year} {make} {model} {trim}"
            photo_url = PHOTO_URLS.get((make, model), FALLBACK_PHOTO)

            # Upsert listing
            await db.execute(text("""
                INSERT INTO listings
                    (id, source_id, external_id, url, title, price, mileage, year, make, model, trim,
                     color_exterior, condition, location_city, location_state, dealer_name,
                     is_active, first_seen_at, last_seen_at)
                VALUES
                    (:id, :source_id, :external_id, :url, :title, :price, :mileage, :year, :make, :model, :trim,
                     :color_exterior, :condition, :location_city, :location_state, :dealer_name,
                     true, NOW(), NOW())
                ON CONFLICT (source_id, external_id) DO UPDATE SET
                    price = EXCLUDED.price,
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
                "condition": "used",
                "location_city": city,
                "location_state": state,
                "dealer_name": "CarMax",
            })

            # Get the actual id after upsert (could differ if conflict)
            result2 = await db.execute(text(
                "SELECT id FROM listings WHERE source_id = :sid AND external_id = :eid"
            ), {"sid": source_id, "eid": stock})
            actual_id = result2.scalar()

            # Insert primary photo (ignore conflict)
            await db.execute(text("""
                INSERT INTO photos (id, listing_id, url, is_primary, sort_order)
                VALUES (:id, :listing_id, :url, true, 0)
                ON CONFLICT DO NOTHING
            """), {"id": str(uuid.uuid4()), "listing_id": str(actual_id), "url": photo_url})

            # Record price history
            await db.execute(text("""
                INSERT INTO price_history (listing_id, price, recorded_at)
                VALUES (:listing_id, :price, NOW())
            """), {"listing_id": str(actual_id), "price": price_cents})

            count += 1

        await db.commit()
        print(f"Seeded {count} listings successfully.")


if __name__ == "__main__":
    asyncio.run(main())
