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
    photo_url = models.URLField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
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


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=40, blank=True)
    ram = models.CharField(max_length=30, blank=True)
    storage = models.CharField(max_length=30, blank=True)
    size = models.CharField(max_length=30, blank=True)
    price_delta = models.FloatField(default=0)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image_url = models.URLField()
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.name} image {self.id}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']


class PromoBanner(models.Model):
    title = models.CharField(max_length=140)
    subtitle = models.CharField(max_length=220, blank=True)
    cta_text = models.CharField(max_length=40, default='Shop now')
    cta_url = models.CharField(max_length=220, default='/')
    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return self.title


class AnalyticsEvent(models.Model):
    EVENT_PRODUCT_VIEW = 'product_view'
    EVENT_ADD_TO_CART = 'add_to_cart'
    EVENT_CHECKOUT_START = 'checkout_start'
    EVENT_ORDER_PLACED = 'order_placed'
    EVENT_CHOICES = [
        (EVENT_PRODUCT_VIEW, 'Product View'),
        (EVENT_ADD_TO_CART, 'Add To Cart'),
        (EVENT_CHECKOUT_START, 'Checkout Start'),
        (EVENT_ORDER_PLACED, 'Order Placed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=40, choices=EVENT_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_name} at {self.created_at:%Y-%m-%d %H:%M}"