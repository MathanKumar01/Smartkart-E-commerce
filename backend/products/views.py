from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Wishlist, ProductVariant, ProductImage, ProductReview, RecentlyViewed, PromoBanner, AnalyticsEvent
from cart.models import Cart
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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


@login_required
def product_list(request):

    category = normalize_category(request.GET.get("category"))
    query = request.GET.get("q")

    products = Product.objects.only(
        "id",
        "name",
        "description",
        "price",
        "original_price",
        "discount_percent",
        "rating",
        "image_url",
        "category",
    ).order_by("id")

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

    cart_products = set()

    if request.user.is_authenticated:
        cart_products = set(
            Cart.objects.filter(user=request.user).values_list("product_id", flat=True)
        )

    paginator = Paginator(products, 24)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    active_banner = PromoBanner.objects.filter(is_active=True).order_by('priority', '-created_at').first()

    return render(request, "products.html", {
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "cart_products": cart_products,
        "selected_category": category,
        "active_banner": active_banner,
    })


@login_required
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    variants = list(ProductVariant.objects.filter(product=product, is_active=True))
    gallery_images = list(ProductImage.objects.filter(product=product))
    reviews = ProductReview.objects.filter(product=product)[:8]

    recommendation_qs = Product.objects.exclude(id=product.id)
    if product.category:
        recommendation_qs = recommendation_qs.filter(category=product.category)
    recommendations = list(recommendation_qs.order_by('-rating', '-id')[:6])

    analytics_user = request.user if request.user.is_authenticated else None
    AnalyticsEvent.objects.create(
        user=analytics_user,
        event_name=AnalyticsEvent.EVENT_PRODUCT_VIEW,
        product=product,
        metadata={'product_id': product.id},
    )

    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={},
        )

    return render(request, "product_detail.html", {
        "product": product,
        "variants": variants,
        "gallery_images": gallery_images,
        "reviews": reviews,
        "recommendations": recommendations,
    })


@login_required
def submit_review(request, product_id):
    if request.method != 'POST':
        return redirect(f'/product/{product_id}/')

    product = get_object_or_404(Product, id=product_id)
    rating_raw = request.POST.get('rating', '0').strip()
    comment = request.POST.get('comment', '').strip()
    photo_url = request.POST.get('photo_url', '').strip()

    try:
        rating = int(rating_raw)
    except ValueError:
        rating = 0

    if rating < 1 or rating > 5:
        messages.error(request, 'Please select a rating between 1 and 5.')
        return redirect(f'/product/{product_id}/')

    has_purchased = Cart.objects.filter(user=request.user, product=product).exists() is False
    # A purchase is inferred if user has at least one matching order.
    from orders.models import Order
    has_purchased = Order.objects.filter(user=request.user, product=product).exists()

    ProductReview.objects.create(
        product=product,
        user=request.user,
        reviewer_name=request.user.username,
        rating=rating,
        comment=comment,
        photo_url=photo_url,
        is_verified_purchase=has_purchased,
    )

    all_reviews = ProductReview.objects.filter(product=product)
    review_count = all_reviews.count()
    avg_rating = 0.0
    if review_count:
        avg_rating = sum(r.rating for r in all_reviews) / review_count
    product.reviews_count = review_count
    product.rating = round(avg_rating, 1)
    product.save(update_fields=['reviews_count', 'rating'])

    messages.success(request, 'Review submitted successfully.')
    return redirect(f'/product/{product_id}/')


@login_required
def add_to_wishlist(request, product_id):

    product = Product.objects.get(id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def wishlist_view(request):

    items = Wishlist.objects.filter(user=request.user)

    return render(request, "wishlist.html", {"items": items})


@login_required
def remove_from_wishlist(request, product_id):

    item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    item.delete()

    return redirect('wishlist')