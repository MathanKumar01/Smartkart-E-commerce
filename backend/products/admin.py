from django.contrib import admin
from .models import Product
from .models import Wishlist

admin.site.register(Wishlist)

admin.site.register(Product)
