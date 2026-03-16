from django.db import transaction
from datetime import timedelta
import random
import string
import csv
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
from cart.models import Cart
from products.models import Product, AnalyticsEvent
from .models import Order, ShippingAddress, Coupon, ReturnRequest


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
        discount_total = float(shipping_details.get('discount_amount', 0) or 0)
        coupon_code = shipping_details.get('coupon_code', '')
        total_before_discount = sum(item['total_price'] for item in item_payloads) or 1
        for item in item_payloads:
            product = products_by_id.get(item['product_id'])
            if not product:
                continue
            proportional_discount = round(discount_total * (item['total_price'] / total_before_discount), 2)
            final_total = max(item['total_price'] - proportional_discount, 0)
            now_ts = timezone.now()
            Order.objects.create(
                user=user,
                product=product,
                quantity=item['quantity'],
                total_price=final_total,
                coupon_code=coupon_code,
                discount_amount=proportional_discount,
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
                ordered_at=now_ts,
            )
        Cart.objects.filter(user=user).delete()


def _validate_coupon(user, code, order_total):
    if not code:
        return 0, ''

    coupon = Coupon.objects.filter(code__iexact=code.strip(), is_active=True).first()
    if not coupon:
        return 0, 'Invalid coupon code.'

    now = timezone.now()
    if coupon.active_from and now < coupon.active_from:
        return 0, 'Coupon is not active yet.'
    if coupon.active_until and now > coupon.active_until:
        return 0, 'Coupon has expired.'
    if coupon.min_order_value and order_total < coupon.min_order_value:
        return 0, f'Minimum order for this coupon is {coupon.min_order_value:.0f}.'
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return 0, 'Coupon usage limit reached.'
    if coupon.first_order_only and Order.objects.filter(user=user).exists():
        return 0, 'This coupon is valid only for your first order.'

    if coupon.discount_type == Coupon.TYPE_PERCENT:
        discount = order_total * (coupon.discount_value / 100.0)
    else:
        discount = coupon.discount_value

    discount = round(min(discount, order_total), 2)
    return discount, ''


def _mark_coupon_usage(code):
    if not code:
        return
    coupon = Coupon.objects.filter(code__iexact=code).first()
    if coupon:
        coupon.used_count += 1
        coupon.save(update_fields=['used_count'])


def _apply_timeline_timestamps(order):
    changed = []
    if order.shipping_status == Order.STATUS_ORDERED and not order.ordered_at:
        order.ordered_at = order.created_at
        changed.append('ordered_at')
    if order.shipping_status in [Order.STATUS_SHIPPED, Order.STATUS_OUT_FOR_DELIVERY, Order.STATUS_DELIVERED] and not order.shipped_at:
        order.shipped_at = order.created_at + timedelta(days=1)
        changed.append('shipped_at')
    if order.shipping_status in [Order.STATUS_OUT_FOR_DELIVERY, Order.STATUS_DELIVERED] and not order.out_for_delivery_at:
        order.out_for_delivery_at = order.created_at + timedelta(days=3)
        changed.append('out_for_delivery_at')
    if order.shipping_status == Order.STATUS_DELIVERED and not order.delivered_at:
        order.delivered_at = order.created_at + timedelta(days=4)
        changed.append('delivered_at')
    if changed:
        order.save(update_fields=changed)


def _upsert_shipping_address(user, shipping_details, label='Home', set_default=False):
    safe_label = (label or 'Home').strip()[:50] or 'Home'
    lookup = {
        'user': user,
        'shipping_name': shipping_details['shipping_name'],
        'phone_number': shipping_details['phone_number'],
        'address_line': shipping_details['address_line'],
        'city': shipping_details['city'],
        'state': shipping_details['state'],
        'postal_code': shipping_details['postal_code'],
    }

    address = ShippingAddress.objects.filter(**lookup).first()
    if address:
        if address.label != safe_label:
            address.label = safe_label
        if set_default and not address.is_default:
            address.is_default = True
        address.save()
        return address

    return ShippingAddress.objects.create(
        label=safe_label,
        is_default=set_default,
        **lookup,
    )


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
    save_address = request.POST.get('save_address') == '1'
    set_default = request.POST.get('set_default') == '1'
    address_label = request.POST.get('address_label', 'Home').strip()
    coupon_code = request.POST.get('coupon_code', '').strip()

    if not all(shipping_details.values()):
        messages.error(request, 'Please fill in full delivery address before checkout.')
        return redirect('/cart/')

    if not shipping_details['phone_number'].isdigit() or len(shipping_details['phone_number']) < 10:
        messages.error(request, 'Please enter a valid phone number (minimum 10 digits).')
        return redirect('/cart/')

    if not shipping_details['postal_code'].isdigit() or len(shipping_details['postal_code']) != 6:
        messages.error(request, 'Please enter a valid 6-digit pincode.')
        return redirect('/cart/')

    if save_address:
        try:
            _upsert_shipping_address(
                user=request.user,
                shipping_details=shipping_details,
                label=address_label,
                set_default=set_default,
            )
        except (OperationalError, ProgrammingError):
            messages.warning(request, 'Address book is not ready yet. Please run migrations and try again.')

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

    discount_amount, coupon_error = _validate_coupon(request.user, coupon_code, total_amount)
    if coupon_error:
        messages.error(request, coupon_error)
        return redirect('/cart/')
    payable_amount = max(total_amount - discount_amount, 0)

    shipping_details['coupon_code'] = coupon_code.upper() if coupon_code else ''
    shipping_details['discount_amount'] = discount_amount

    AnalyticsEvent.objects.create(
        user=request.user,
        event_name=AnalyticsEvent.EVENT_CHECKOUT_START,
        product=None,
        metadata={
            'cart_total': total_amount,
            'discount': discount_amount,
            'payable': payable_amount,
            'coupon': shipping_details['coupon_code'],
        },
    )

    # COD — create orders immediately, no payment page needed
    if selected_payment_method == Order.PAYMENT_METHOD_COD:
        _create_orders_from_items(
            user=request.user,
            item_payloads=item_payloads,
            payment_method=selected_payment_method,
            shipping_details=shipping_details,
        )
        _mark_coupon_usage(shipping_details['coupon_code'])
        AnalyticsEvent.objects.create(
            user=request.user,
            event_name=AnalyticsEvent.EVENT_ORDER_PLACED,
            metadata={'coupon': shipping_details['coupon_code'], 'amount': payable_amount},
        )
        return redirect('/orders/')

    # UPI / Card — show mock payment page
    request.session['pending_payment'] = {
        'method': selected_payment_method,
        'items': item_payloads,
        'amount': payable_amount,
        'base_amount': total_amount,
        'discount_amount': discount_amount,
        'coupon_code': shipping_details['coupon_code'],
        'shipping': shipping_details,
    }

    return render(request, 'payment_checkout.html', {
        'amount_display': payable_amount,
        'base_amount': total_amount,
        'discount_amount': discount_amount,
        'coupon_code': shipping_details['coupon_code'],
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
    _mark_coupon_usage(pending_payment.get('coupon_code', ''))
    AnalyticsEvent.objects.create(
        user=request.user,
        event_name=AnalyticsEvent.EVENT_ORDER_PLACED,
        metadata={
            'coupon': pending_payment.get('coupon_code', ''),
            'amount': pending_payment.get('amount', 0),
        },
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
        _apply_timeline_timestamps(order)
        order.tracking_step = status_rank[order.shipping_status]
        order.can_request_return = order.shipping_status == Order.STATUS_DELIVERED

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
    _apply_timeline_timestamps(order)

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


@login_required
def cancel_order(request, order_id):
    order = Order.objects.filter(user=request.user, id=order_id).first()
    if not order:
        return redirect('/orders/')
    if order.shipping_status in [Order.STATUS_ORDERED, Order.STATUS_SHIPPED] and not order.is_cancelled:
        order.is_cancelled = True
        order.cancelled_at = timezone.now()
        order.save(update_fields=['is_cancelled', 'cancelled_at'])
        messages.success(request, 'Order cancelled successfully.')
    elif order.is_cancelled:
        messages.info(request, 'Order is already cancelled.')
    else:
        messages.error(request, 'This order can no longer be cancelled.')
    return redirect('/orders/')


@login_required
def request_return(request, order_id):
    order = Order.objects.filter(user=request.user, id=order_id).first()
    if not order:
        return redirect('/orders/')
    reason = request.POST.get('reason', '').strip()
    if request.method == 'POST' and reason:
        ReturnRequest.objects.create(order=order, user=request.user, reason=reason)
        messages.success(request, 'Return request submitted.')
    return redirect('/orders/')


@login_required
def set_default_address(request, address_id):
    address = ShippingAddress.objects.filter(user=request.user, id=address_id).first()
    if address:
        ShippingAddress.objects.filter(user=request.user, is_default=True).exclude(id=address.id).update(is_default=False)
        address.is_default = True
        address.save(update_fields=['is_default'])
    return redirect('/cart/')


@login_required
def delete_address(request, address_id):
    address = ShippingAddress.objects.filter(user=request.user, id=address_id).first()
    if address:
        was_default = address.is_default
        address.delete()
        if was_default:
            fallback = ShippingAddress.objects.filter(user=request.user).order_by('-updated_at', '-created_at').first()
            if fallback:
                fallback.is_default = True
                fallback.save(update_fields=['is_default'])
    return redirect('/cart/')


@login_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Product', 'Qty', 'Total', 'Payment', 'Status', 'Created'])
    for order in Order.objects.filter(user=request.user).order_by('-created_at'):
        writer.writerow([
            order.id,
            order.product.name,
            order.quantity,
            order.total_price,
            order.get_payment_method_display(),
            order.get_shipping_status_display(),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response