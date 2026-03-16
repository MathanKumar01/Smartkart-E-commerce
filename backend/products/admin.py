from django.contrib import admin
from .models import Product, ProductReview, Wishlist, ProductVariant, ProductImage, RecentlyViewed, PromoBanner, AnalyticsEvent


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'category',
		'price',
		'discount_percent',
		'rating',
		'reviews_count',
		'stock',
	)
	search_fields = ('name', 'description', 'category')
	list_filter = ('category',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
	list_display = ('product', 'rating', 'reviewer_name', 'user', 'is_verified_purchase', 'created_at')
	search_fields = ('product__name', 'reviewer_name', 'comment', 'user__username')
	list_filter = ('rating', 'created_at')


admin.site.register(Wishlist)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ('product', 'name', 'color', 'ram', 'storage', 'size', 'price_delta', 'stock', 'is_active')
	list_filter = ('is_active',)
	search_fields = ('product__name', 'name', 'color', 'ram', 'storage', 'size')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ('product', 'sort_order', 'image_url')
	search_fields = ('product__name', 'image_url')


@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
	list_display = ('title', 'priority', 'is_active', 'created_at')
	list_filter = ('is_active',)
	search_fields = ('title', 'subtitle')


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
	list_display = ('event_name', 'user', 'product', 'created_at')
	list_filter = ('event_name', 'created_at')
	search_fields = ('user__username', 'product__name')


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
	list_display = ('user', 'product', 'viewed_at')
	search_fields = ('user__username', 'product__name')
