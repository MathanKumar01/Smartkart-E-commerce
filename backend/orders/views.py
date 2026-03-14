from django.shortcuts import redirect
from cart.models import Cart
from .models import Order


def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    for item in cart_items:

        Order.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            total_price=item.product.price * item.quantity
        )

    cart_items.delete()

    return redirect('/orders/')

from django.shortcuts import render
from .models import Order


def order_list(request):

    orders = Order.objects.filter(user=request.user)

    return render(request, 'orders.html', {'orders': orders})