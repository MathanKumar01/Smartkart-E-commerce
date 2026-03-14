from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart_view, name='cart'),
    path('increase/<int:cart_id>/', views.increase_quantity),
    path('decrease/<int:cart_id>/', views.decrease_quantity),
    path('remove/<int:cart_id>/', views.remove_item),
    
]