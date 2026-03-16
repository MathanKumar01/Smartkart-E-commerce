from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_product_feature_pack"),
        ("cart", "0002_alter_cart_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="variant",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="products.productvariant"),
        ),
        migrations.AlterUniqueTogether(
            name="cart",
            unique_together={("user", "product", "variant")},
        ),
    ]
