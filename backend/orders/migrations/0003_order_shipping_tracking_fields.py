from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address_line",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="order",
            name="city",
            field=models.CharField(default="", max_length=80),
        ),
        migrations.AddField(
            model_name="order",
            name="expected_delivery_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="phone_number",
            field=models.CharField(default="", max_length=15),
        ),
        migrations.AddField(
            model_name="order",
            name="postal_code",
            field=models.CharField(default="", max_length=10),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_name",
            field=models.CharField(default="", max_length=120),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_status",
            field=models.CharField(
                choices=[
                    ("ordered", "Ordered"),
                    ("shipped", "Shipped"),
                    ("out_for_delivery", "Out for Delivery"),
                    ("delivered", "Delivered"),
                ],
                default="ordered",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="state",
            field=models.CharField(default="", max_length=80),
        ),
        migrations.AddField(
            model_name="order",
            name="tracking_id",
            field=models.CharField(default="", max_length=30),
        ),
    ]
