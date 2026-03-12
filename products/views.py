from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Product
from cart.models import Cart
from .models import Wishlist
from django.shortcuts import redirect


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products}) 
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    return render(request, "product_detail.html", {"product": product})

def product_list(request):

    products = Product.objects.all()

    cart_products = []

    if request.user.is_authenticated:
        cart_products = Cart.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, "products.html", {
        "products": products,
        "cart_products": cart_products
    })
def add_to_wishlist(request, product_id):

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))

def wishlist_view(request):

    items = Wishlist.objects.filter(user=request.user)

    return render(request, "wishlist.html", {"items": items})

def remove_from_wishlist(request, product_id):

    item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    item.delete()

    return redirect('wishlist')