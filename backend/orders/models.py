from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):

    PAYMENT_METHOD_COD = 'cod'
    PAYMENT_METHOD_UPI = 'upi'
    PAYMENT_METHOD_CARD = 'card'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_COD, 'Cash on Delivery'),
        (PAYMENT_METHOD_UPI, 'UPI'),
        (PAYMENT_METHOD_CARD, 'Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    total_price = models.FloatField()
    coupon_code = models.CharField(max_length=40, blank=True)
    discount_amount = models.FloatField(default=0)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_COD,
    )

    STATUS_ORDERED = 'ordered'
    STATUS_SHIPPED = 'shipped'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    SHIPPING_STATUS_CHOICES = [
        (STATUS_ORDERED, 'Ordered'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_OUT_FOR_DELIVERY, 'Out for Delivery'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    shipping_name = models.CharField(max_length=120, default='')
    phone_number = models.CharField(max_length=15, default='')
    address_line = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=80, default='')
    state = models.CharField(max_length=80, default='')
    postal_code = models.CharField(max_length=10, default='')

    tracking_id = models.CharField(max_length=30, default='')
    shipping_status = models.CharField(
        max_length=20,
        choices=SHIPPING_STATUS_CHOICES,
        default=STATUS_ORDERED,
    )
    expected_delivery_date = models.DateField(null=True, blank=True)
    ordered_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    label = models.CharField(max_length=50, default='Home')
    shipping_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_default:
            ShippingAddress.objects.filter(user=self.user).exclude(id=self.id).update(is_default=False)
        elif not ShippingAddress.objects.filter(user=self.user, is_default=True).exists():
            ShippingAddress.objects.filter(id=self.id).update(is_default=True)
            self.is_default = True

    def __str__(self):
        return f"{self.user.username} - {self.label}"


class Coupon(models.Model):
    TYPE_PERCENT = 'percent'
    TYPE_FIXED = 'fixed'
    DISCOUNT_TYPE_CHOICES = [
        (TYPE_PERCENT, 'Percent'),
        (TYPE_FIXED, 'Fixed Amount'),
    ]

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=TYPE_PERCENT)
    discount_value = models.FloatField()
    min_order_value = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    first_order_only = models.BooleanField(default=False)
    usage_limit = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    active_from = models.DateTimeField(null=True, blank=True)
    active_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code.upper()


class ReturnRequest(models.Model):
    STATUS_REQUESTED = 'requested'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'Requested'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=300)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Return #{self.id} for order {self.order_id}"