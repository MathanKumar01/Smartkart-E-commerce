from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from products.models import ProductVariant

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product', 'variant')

    def __str__(self):
        return self.product.name