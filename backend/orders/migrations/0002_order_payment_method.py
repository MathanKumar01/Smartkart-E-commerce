from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("cod", "Cash on Delivery"),
                    ("upi", "UPI"),
                    ("card", "Card"),
                ],
                default="cod",
                max_length=20,
            ),
        ),
    ]
