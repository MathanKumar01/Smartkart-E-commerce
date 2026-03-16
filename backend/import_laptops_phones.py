"""
Import 10 laptops and 10 phones from Flipkart CSVs.
Uses actual Rating and Discount from the CSV data.
"""
import os
import re
import django
import pandas as pd
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product

MOBILE_CSV  = r"C:\Users\MathanVini\Downloads\flipkart_mobile_data.csv"
LAPTOP_CSV  = r"C:\Users\MathanVini\Downloads\flipkart_laptops (1).csv"


def parse_price(val):
    """'₹6,499' → 6499.0"""
    try:
        return float(str(val).replace("₹", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


def parse_discount(val):
    """'35% off' → 35"""
    try:
        m = re.search(r"(\d+)", str(val))
        return int(m.group(1)) if m else 0
    except Exception:
        return 0


def parse_rating(val):
    """'4.2' → 4.2, bad value → random 3.5–4.8"""
    try:
        r = float(str(val).strip())
        if 1.0 <= r <= 5.0:
            return round(r, 1)
    except (ValueError, TypeError):
        pass
    return round(random.uniform(3.5, 4.8), 1)


def parse_reviews(val):
    """'58,788 Ratings & 3,425 Reviews' → 3425"""
    try:
        m = re.search(r"([\d,]+)\s*Review", str(val), re.I)
        if m:
            return int(m.group(1).replace(",", ""))
    except Exception:
        pass
    return random.randint(50, 5000)


def parse_description(val):
    """Clean up the Key Features list string."""
    s = str(val).strip().strip("[]").replace("'", "").replace('"', "")
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return "\n".join(parts)


def import_rows(df, category, count=10):
    df = df.dropna(subset=["Title", "Image URL", "Price"])
    sample = df.sample(n=min(count, len(df)), random_state=None)

    imported = 0
    for _, row in sample.iterrows():
        price        = parse_price(row.get("Price", 0))
        orig_price   = parse_price(row.get("Original Price", price))
        discount     = parse_discount(row.get("Discount", "0"))
        rating       = parse_rating(row.get("Rating", 0))
        reviews_col  = "Ratings & Reviews\n"          # column has trailing newline
        reviews      = parse_reviews(row.get(reviews_col, row.get("Ratings & Reviews", 0)))
        description  = parse_description(row.get("Key Features", ""))
        image_url    = str(row.get("Image URL", "")).strip()
        name         = str(row.get("Title", "Product")).strip()[:200]

        if not image_url or not name:
            continue

        # Ensure original_price is never less than price
        if orig_price < price:
            orig_price = price

        # Recalculate discount if not from CSV
        if discount == 0 and orig_price > price:
            discount = int(round(((orig_price - price) / orig_price) * 100))

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            original_price=orig_price,
            discount_percent=discount,
            rating=rating,
            reviews_count=reviews,
            stock=random.randint(5, 50),
            image_url=image_url,
            category=category,
        )
        print(f"  [{category}] {name[:60]} | ₹{price} | {discount}% off | ⭐ {rating} | {reviews} reviews")
        imported += 1

    return imported


print("=" * 60)
print("Importing 10 LAPTOPS...")
df_laptops = pd.read_csv(LAPTOP_CSV)
n_laptops  = import_rows(df_laptops, "laptop", 10)
print(f"  → Imported {n_laptops} laptops\n")

print("Importing 10 PHONES...")
df_phones = pd.read_csv(MOBILE_CSV)
n_phones  = import_rows(df_phones, "phone", 10)
print(f"  → Imported {n_phones} phones\n")

print("=" * 60)
print(f"Done! Total new products added: {n_laptops + n_phones}")
print(f"Total products in DB: {Product.objects.count()}")
