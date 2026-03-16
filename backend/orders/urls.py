from django.urls import path
from . import views

urlpatterns = [

    path('', views.order_list),

    path('checkout/', views.checkout),

    path('payment/success/', views.payment_success),

    path('payment/failed/', views.payment_failed),

    path('payment/cancel/', views.payment_cancel),

    path('track/<int:order_id>/', views.order_track),

]