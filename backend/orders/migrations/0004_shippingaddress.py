from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_order_shipping_tracking_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShippingAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(default="Home", max_length=50)),
                ("shipping_name", models.CharField(max_length=120)),
                ("phone_number", models.CharField(max_length=15)),
                ("address_line", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=80)),
                ("state", models.CharField(max_length=80)),
                ("postal_code", models.CharField(max_length=10)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping_addresses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-is_default", "-updated_at"],
            },
        ),
    ]
