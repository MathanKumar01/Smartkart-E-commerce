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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username