from django.core.management.base import BaseCommand
import re

from products.models import Product


class Command(BaseCommand):
    help = "Convert Product.image_url entries from http:// to https:// to avoid mixed-content blocking."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many rows would be updated without saving changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        products = Product.objects.exclude(image_url="").only("id", "image_url")
        to_update = []

        for product in products.iterator(chunk_size=500):
            normalized_url = product.image_url

            if normalized_url.startswith("http://"):
                normalized_url = normalized_url.replace("http://", "https://", 1)

            normalized_url = re.sub(
                r"^https://img\d+a?\.flixcart\.com/",
                "https://rukminim2.flixcart.com/",
                normalized_url,
                flags=re.IGNORECASE,
            )

            if normalized_url != product.image_url:
                to_update.append((product.id, normalized_url))

        count = len(to_update)

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No image URL normalization changes needed."))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"Dry run: {count} product image URL(s) would be normalized.")
            )
            return

        updated = 0
        for product_id, normalized_url in to_update:
            product = Product(id=product_id, image_url=normalized_url)
            product.save(update_fields=["image_url"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Normalized {updated} product image URL(s)."))
