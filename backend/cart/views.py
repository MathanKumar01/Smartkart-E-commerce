from django.shortcuts import redirect
from .models import Cart
from django.shortcuts import redirect, get_object_or_404
from products.models import Product
from django.contrib.auth.models import User
from django.shortcuts import render

from django.shortcuts import redirect
from .models import Cart
from products.models import Product

def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, product=product, quantity=1)

    return redirect(request.META.get('HTTP_REFERER', '/'))

from .models import Cart

def cart_view(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    cart_count = cart_items.count()

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
        "cart_count": cart_count
    })
def increase_quantity(request, cart_id):

    cart = Cart.objects.get(id=cart_id)
    cart.quantity += 1
    cart.save()

    return redirect('/cart/')


def decrease_quantity(request, cart_id):

    cart = Cart.objects.get(id=cart_id)

    if cart.quantity > 1:
        cart.quantity -= 1
        cart.save()

    return redirect('/cart/')


def remove_item(request, cart_id):

    cart = Cart.objects.get(id=cart_id)
    cart.delete()

    return redirect('/cart/')