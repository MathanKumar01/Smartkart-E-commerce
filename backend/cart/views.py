from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError, ProgrammingError
from .models import Cart
from products.models import Product, ProductVariant, AnalyticsEvent
from orders.models import ShippingAddress

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    variant_id = request.GET.get('variant')
    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product, is_active=True).first()

    cart_item = Cart.objects.filter(user=request.user, product=product, variant=variant).first()

    available_stock = product.stock
    if variant:
        available_stock = variant.stock

    if cart_item:
        if cart_item.quantity < max(available_stock, 0):
            cart_item.quantity += 1
            cart_item.save()
    else:
        if available_stock > 0:
            Cart.objects.create(user=request.user, product=product, variant=variant, quantity=1)

    AnalyticsEvent.objects.create(
        user=request.user,
        event_name=AnalyticsEvent.EVENT_ADD_TO_CART,
        product=product,
        metadata={
            'variant_id': variant.id if variant else None,
        },
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def cart_view(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    cart_count = cart_items.count()
    try:
        saved_addresses = list(
            ShippingAddress.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
        )
    except (OperationalError, ProgrammingError):
        # Address table may not exist yet if migrations are pending.
        saved_addresses = []
    default_address = next((addr for addr in saved_addresses if addr.is_default), None)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
        "cart_count": cart_count,
        "saved_addresses": saved_addresses,
        "default_address": default_address,
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