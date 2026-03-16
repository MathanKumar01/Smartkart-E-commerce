from django.urls import path
from . import views

urlpatterns = [

    path('', views.order_list),

    path('checkout/', views.checkout),

    path('payment/success/', views.payment_success),

    path('payment/failed/', views.payment_failed),

    path('payment/cancel/', views.payment_cancel),

    path('track/<int:order_id>/', views.order_track),
    path('cancel/<int:order_id>/', views.cancel_order),
    path('return/<int:order_id>/', views.request_return),
    path('address/default/<int:address_id>/', views.set_default_address),
    path('address/delete/<int:address_id>/', views.delete_address),
    path('export/csv/', views.export_orders_csv),

]