from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Product(models.Model):

    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('phone', 'Phone'),
        ('accessories', 'Accessories'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    original_price = models.FloatField(null=True, blank=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    reviews_count = models.PositiveIntegerField(default=0)
    stock = models.IntegerField()

    image_url = models.URLField()

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewer_name = models.CharField(max_length=120, blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        label = self.reviewer_name or (self.user.username if self.user else 'Anonymous')
        return f"{self.product.name} - {label} ({self.rating}/5)"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name