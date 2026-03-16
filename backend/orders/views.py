from django.db import transaction
from datetime import timedelta
import random
import string
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from cart.models import Cart
from products.models import Product
from .models import Order


def _generate_tracking_id():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"SC{code}"


def _resolve_shipping_status(order):
    days_since_order = (timezone.now().date() - order.created_at.date()).days
    if days_since_order >= 4:
        return Order.STATUS_DELIVERED
    if days_since_order >= 3:
        return Order.STATUS_OUT_FOR_DELIVERY
    if days_since_order >= 1:
        return Order.STATUS_SHIPPED
    return Order.STATUS_ORDERED


def _hydrate_legacy_order_fields(order):
    update_fields = []

    if not order.tracking_id:
        order.tracking_id = _generate_tracking_id()
        update_fields.append('tracking_id')

    if not order.expected_delivery_date:
        order.expected_delivery_date = order.created_at.date() + timedelta(days=4)
        update_fields.append('expected_delivery_date')

    resolved_status = _resolve_shipping_status(order)
    if order.shipping_status != resolved_status:
        order.shipping_status = resolved_status
        update_fields.append('shipping_status')

    if update_fields:
        order.save(update_fields=update_fields)


def _create_orders_from_items(user, item_payloads, payment_method, shipping_details):
    product_ids = [item['product_id'] for item in item_payloads]
    products_by_id = {
        product.id: product for product in Product.objects.filter(id__in=product_ids)
    }

    expected_delivery_date = timezone.now().date() + timedelta(days=random.randint(3, 4))

    with transaction.atomic():
        for item in item_payloads:
            product = products_by_id.get(item['product_id'])
            if not product:
                continue
            Order.objects.create(
                user=user,
                product=product,
                quantity=item['quantity'],
                total_price=item['total_price'],
                payment_method=payment_method,
                shipping_name=shipping_details['shipping_name'],
                phone_number=shipping_details['phone_number'],
                address_line=shipping_details['address_line'],
                city=shipping_details['city'],
                state=shipping_details['state'],
                postal_code=shipping_details['postal_code'],
                tracking_id=_generate_tracking_id(),
                shipping_status=Order.STATUS_ORDERED,
                expected_delivery_date=expected_delivery_date,
            )
        Cart.objects.filter(user=user).delete()


@login_required
def checkout(request):

    if request.method != 'POST':
        return redirect('/cart/')

    selected_payment_method = request.POST.get(
        'payment_method',
        Order.PAYMENT_METHOD_COD,
    )
    allowed_payment_methods = {
        choice[0] for choice in Order.PAYMENT_METHOD_CHOICES
    }
    if selected_payment_method not in allowed_payment_methods:
        selected_payment_method = Order.PAYMENT_METHOD_COD

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('/cart/')

    shipping_details = {
        'shipping_name': request.POST.get('shipping_name', '').strip(),
        'phone_number': request.POST.get('phone_number', '').strip(),
        'address_line': request.POST.get('address_line', '').strip(),
        'city': request.POST.get('city', '').strip(),
        'state': request.POST.get('state', '').strip(),
        'postal_code': request.POST.get('postal_code', '').strip(),
    }

    if not all(shipping_details.values()):
        messages.error(request, 'Please fill in full delivery address before checkout.')
        return redirect('/cart/')

    if not shipping_details['phone_number'].isdigit() or len(shipping_details['phone_number']) < 10:
        messages.error(request, 'Please enter a valid phone number (minimum 10 digits).')
        return redirect('/cart/')

    if not shipping_details['postal_code'].isdigit() or len(shipping_details['postal_code']) != 6:
        messages.error(request, 'Please enter a valid 6-digit pincode.')
        return redirect('/cart/')

    item_payloads = []
    total_amount = 0
    for item in cart_items:
        line_total = item.product.price * item.quantity
        total_amount += line_total
        item_payloads.append({
            'product_id': item.product.id,
            'quantity': item.quantity,
            'total_price': line_total,
        })

    # COD — create orders immediately, no payment page needed
    if selected_payment_method == Order.PAYMENT_METHOD_COD:
        _create_orders_from_items(
            user=request.user,
            item_payloads=item_payloads,
            payment_method=selected_payment_method,
            shipping_details=shipping_details,
        )
        return redirect('/orders/')

    # UPI / Card — show mock payment page
    request.session['pending_payment'] = {
        'method': selected_payment_method,
        'items': item_payloads,
        'amount': total_amount,
        'shipping': shipping_details,
    }

    return render(request, 'payment_checkout.html', {
        'amount_display': total_amount,
        'payment_method': selected_payment_method,
        'user_name': request.user.get_full_name() or request.user.username,
    })


@login_required
def payment_success(request):
    if request.method != 'POST':
        return redirect('/cart/')

    pending_payment = request.session.get('pending_payment')
    if not pending_payment:
        return redirect('/cart/')

    _create_orders_from_items(
        user=request.user,
        item_payloads=pending_payment['items'],
        payment_method=pending_payment['method'],
        shipping_details=pending_payment['shipping'],
    )
    request.session.pop('pending_payment', None)
    return redirect('/orders/')


@login_required
def payment_failed(request):
    request.session.pop('pending_payment', None)
    return render(request, 'payment_failed.html')


@login_required
def payment_cancel(request):
    request.session.pop('pending_payment', None)
    return redirect('/cart/')


@login_required
def order_list(request):

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    status_rank = {
        Order.STATUS_ORDERED: 1,
        Order.STATUS_SHIPPED: 2,
        Order.STATUS_OUT_FOR_DELIVERY: 3,
        Order.STATUS_DELIVERED: 4,
    }

    for order in orders:
        _hydrate_legacy_order_fields(order)
        order.tracking_step = status_rank[order.shipping_status]

    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'orders.html', {
        'orders': orders,
        'total_spent': total_spent,
    })


@login_required
def order_track(request, order_id):
    order = Order.objects.filter(user=request.user, id=order_id).first()
    if not order:
        return redirect('/orders/')

    _hydrate_legacy_order_fields(order)

    status_rank = {
        Order.STATUS_ORDERED: 1,
        Order.STATUS_SHIPPED: 2,
        Order.STATUS_OUT_FOR_DELIVERY: 3,
        Order.STATUS_DELIVERED: 4,
    }
    order.tracking_step = status_rank[order.shipping_status]

    return render(request, 'order_track.html', {
        'order': order,
    })