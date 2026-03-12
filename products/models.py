from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):

    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('phone', 'Phone'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name

    def __str__(self):
        return self.name