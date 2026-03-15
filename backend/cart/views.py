from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Cart
from products.models import Product

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item = Cart.objects.filter(user=request.user, product=product).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        Cart.objects.create(user=request.user, product=product, quantity=1)

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
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


@login_required
def increase_quantity(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart.quantity += 1
    cart.save()

    return redirect('/cart/')


@login_required
def decrease_quantity(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)

    if cart.quantity > 1:
        cart.quantity -= 1
        cart.save()

    return redirect('/cart/')


@login_required
def remove_item(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart.delete()

    return redirect('/cart/')