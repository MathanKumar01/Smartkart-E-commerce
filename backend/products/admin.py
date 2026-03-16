from django.contrib import admin
from .models import Product, ProductReview, Wishlist


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
	list_display = ('product', 'rating', 'reviewer_name', 'user', 'created_at')
	search_fields = ('product__name', 'reviewer_name', 'comment', 'user__username')
	list_filter = ('rating', 'created_at')


admin.site.register(Wishlist)
