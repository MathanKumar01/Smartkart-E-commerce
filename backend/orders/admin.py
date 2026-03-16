from django.contrib import admin
from .models import Order, ShippingAddress, Coupon, ReturnRequest

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'payment_method', 'shipping_status', 'created_at')
	list_filter = ('payment_method', 'shipping_status', 'created_at')
	search_fields = ('user__username', 'product__name', 'tracking_id')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'label', 'shipping_name', 'city', 'state', 'postal_code', 'is_default', 'updated_at')
	list_filter = ('is_default', 'state', 'updated_at')
	search_fields = ('user__username', 'shipping_name', 'phone_number', 'address_line', 'city', 'postal_code')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ('code', 'discount_type', 'discount_value', 'min_order_value', 'first_order_only', 'is_active', 'used_count', 'usage_limit')
	list_filter = ('discount_type', 'first_order_only', 'is_active')
	search_fields = ('code',)


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
	list_display = ('id', 'order', 'user', 'status', 'requested_at', 'resolved_at')
	list_filter = ('status', 'requested_at')
	search_fields = ('order__id', 'user__username', 'reason')
