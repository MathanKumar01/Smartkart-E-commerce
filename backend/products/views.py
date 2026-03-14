from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Wishlist
from cart.models import Cart
from django.db.models import Q


CATEGORY_ALIASES = {
    "accesories": "accessories",
    "accessory": "accessories",
    "mobile": "phone",
    "mobiles": "phone",
    "phones": "phone",
    "laptops": "laptop",
}


def normalize_category(raw_value):
    if not raw_value:
        return ""
    value = raw_value.strip().lower()
    return CATEGORY_ALIASES.get(value, value)

def product_list(request):

    category = normalize_category(request.GET.get("category"))
    query = request.GET.get("q")

    products = Product.objects.all()

    if category:
        if category == "accessories":
            products = products.filter(category__in=["accessories", "accesories"])
        else:
            products = products.filter(category__iexact=category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    cart_products = []

    if request.user.is_authenticated:
        cart_products = Cart.objects.filter(user=request.user)\
            .values_list("product_id", flat=True)

    return render(request, "products.html", {
        "products": products,
        "cart_products": cart_products,
        "selected_category": category,
    })

def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    return render(request, "product_detail.html", {
        "product": product
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