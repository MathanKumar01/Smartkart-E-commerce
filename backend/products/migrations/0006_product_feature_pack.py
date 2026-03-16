from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_product_review_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="productreview",
            name="is_verified_purchase",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="productreview",
            name="photo_url",
            field=models.URLField(blank=True),
        ),
        migrations.CreateModel(
            name="AnalyticsEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_name",
                    models.CharField(
                        choices=[
                            ("product_view", "Product View"),
                            ("add_to_cart", "Add To Cart"),
                            ("checkout_start", "Checkout Start"),
                            ("order_placed", "Order Placed"),
                        ],
                        max_length=40,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="products.product"),
                ),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image_url", models.URLField()),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="gallery_images", to="products.product"),
                ),
            ],
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("color", models.CharField(blank=True, max_length=40)),
                ("ram", models.CharField(blank=True, max_length=30)),
                ("storage", models.CharField(blank=True, max_length=30)),
                ("size", models.CharField(blank=True, max_length=30)),
                ("price_delta", models.FloatField(default=0)),
                ("stock", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="products.product"),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="PromoBanner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=140)),
                ("subtitle", models.CharField(blank=True, max_length=220)),
                ("cta_text", models.CharField(default="Shop now", max_length=40)),
                ("cta_url", models.CharField(default="/", max_length=220)),
                ("is_active", models.BooleanField(default=True)),
                ("priority", models.PositiveSmallIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["priority", "-created_at"]},
        ),
        migrations.CreateModel(
            name="RecentlyViewed",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("viewed_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="products.product"),
                ),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recently_viewed_products", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-viewed_at"], "unique_together": {("user", "product")}},
        ),
    ]
