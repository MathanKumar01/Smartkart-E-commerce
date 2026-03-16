import os
import argparse
import ast
import django
import pandas as pd
from django.db import close_old_connections
from django.db.utils import InterfaceError, OperationalError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), "smartkart_products_clean.csv")

CATEGORY_ALIASES = {
    "accesories": "accessories",
    "accessory": "accessories",
    "mobile": "phone",
    "mobiles": "phone",
    "phones": "phone",
    "laptops": "laptop",
}


def normalize_category(raw_value):
    if pd.isna(raw_value):
        return "accessories"
    value = str(raw_value).strip().lower()
    normalized = CATEGORY_ALIASES.get(value, value)
    if normalized in {"laptop", "phone", "accessories"}:
        return normalized
    return "accessories"


def to_float(value, default=0.0):
    if pd.isna(value):
        return float(default)
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return float(default)


def parse_rating(value):
    if pd.isna(value):
        return 0.0
    text = str(value).strip().lower()
    if "no rating" in text:
        return 0.0
    return max(0.0, min(5.0, to_float(text, default=0.0)))


def parse_image_url(raw_value):
    if pd.isna(raw_value):
        return "https://placehold.co/400x300?text=No+Image"

    text = str(raw_value).strip()
    if not text:
        return "https://placehold.co/400x300?text=No+Image"

    if text.startswith("["):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list) and parsed:
                first_url = str(parsed[0]).strip()
                if first_url:
                    return first_url
        except (SyntaxError, ValueError):
            pass

    return text


def calculate_discount_percent(retail_price, discounted_price):
    if retail_price <= 0 or discounted_price >= retail_price:
        return 0
    discount = ((retail_price - discounted_price) / retail_price) * 100
    return int(round(discount))


def create_product_with_retry(payload, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            Product.objects.create(**payload)
            return True
        except (OperationalError, InterfaceError) as exc:
            close_old_connections()
            if attempt == max_retries:
                print(f"DB error after {max_retries} retries: {exc}")
                return False
            print(f"DB connection issue, retrying row (attempt {attempt + 1}/{max_retries})...")


def import_products(csv_path, delete_existing=False, limit=None):
    if delete_existing:
        deleted_count, _ = Product.objects.all().delete()
        print(f"Deleted existing records: {deleted_count}")
    elif Product.objects.exists():
        print("Products already exist. Use --delete-existing to replace them.")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if limit:
        df = df.head(limit)

    created_count = 0
    skipped_count = 0

    for _, row in df.iterrows():
        retail_price = to_float(row.get("retail_price"), default=0.0)
        discounted_price = to_float(row.get("discounted_price"), default=retail_price)
        final_price = discounted_price if discounted_price > 0 else retail_price

        payload = dict(
            name=str(row.get("product_name", "Unnamed Product"))[:200],
            description=str(row.get("description", "")).strip(),
            price=final_price,
            original_price=retail_price if retail_price > 0 else None,
            discount_percent=calculate_discount_percent(retail_price, final_price),
            rating=parse_rating(row.get("product_rating")),
            reviews_count=0,
            stock=10,
            image_url=parse_image_url(row.get("image")),
            category=normalize_category(row.get("category")),
        )
        if create_product_with_retry(payload):
            created_count += 1
        else:
            skipped_count += 1

    print(f"Imported products: {created_count}")
    if skipped_count:
        print(f"Skipped products due persistent DB errors: {skipped_count}")


def main():
    parser = argparse.ArgumentParser(description="Import SmartCart products from cleaned CSV")
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV_PATH,
        help=f"Path to cleaned CSV file (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--delete-existing",
        action="store_true",
        help="Delete existing products before importing",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Import only the first N rows",
    )
    args = parser.parse_args()

    import_products(csv_path=args.csv, delete_existing=args.delete_existing, limit=args.limit)


if __name__ == "__main__":
    main()