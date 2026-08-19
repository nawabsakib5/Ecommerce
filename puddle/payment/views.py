import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
import requests as http_requests


from item.models import Item
from .models import PaymentMethod, Transaction, Order


# ── Helper: IP address ──
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ── Checkout Page ──
@login_required
def checkout(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    if item.user == request.user:
        messages.error(request, "You cannot buy your own item.")
        return redirect('item:detail', pk=item_pk)

    if item.is_sold or item.status != 'active':
        messages.error(request, "This item is no longer available.")
        return redirect('item:detail', pk=item_pk)

    # User এর saved payment methods
    saved_methods = PaymentMethod.objects.filter(
        user=request.user,
        is_active=True
    )

    price = item.sale_price if item.is_on_sale else item.original_price

    return render(request, 'payment/checkout.html', {
        'item': item,
        'price': price,
        'saved_methods': saved_methods,
    })


# ── Initiate Payment ──
@login_required
@require_POST
def initiate_payment(request, item_pk):
    item = get_object_or_404(Item, pk=item_pk)

    if item.user == request.user:
        messages.error(request, "You cannot buy your own item.")
        return redirect('payment:checkout', item_pk=item_pk)

    if item.is_sold or item.status != 'active':
        messages.error(request, "This item is no longer available.")
        return redirect('item:detail', pk=item_pk)

    payment_type = request.POST.get('payment_type')
    delivery_name = request.POST.get('delivery_name', '').strip()
    delivery_phone = request.POST.get('delivery_phone', '').strip()
    delivery_address = request.POST.get('delivery_address', '').strip()
    notes = request.POST.get('notes', '').strip()
    delivery_zone = request.POST.get('delivery_zone', 'dhaka')
    free_delivery = request.POST.get('free_delivery', '0') == '1'

    # Quantity validate
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        if quantity > item.stock_count:
            messages.error(request, f"Only {item.stock_count} items available.")
            return redirect('payment:checkout', item_pk=item_pk)
    except (ValueError, TypeError):
        quantity = 1

    if not all([payment_type, delivery_name, delivery_phone, delivery_address]):
        messages.error(request, "Please fill all delivery information.")
        return redirect('payment:checkout', item_pk=item_pk)

    # Free delivery — শুধু seller বা admin দিতে পারবে
    if free_delivery and not (request.user.user_type == 'Seller' or request.user.is_staff):
        free_delivery = False

    # Delivery charge — Steadfast
    if free_delivery:
        delivery_charge = 0
    elif delivery_zone == 'outside':
        delivery_charge = 150
    else:
        delivery_charge = 80

    # Price calculation
    unit_price = item.sale_price if item.is_on_sale else item.original_price
    subtotal = unit_price * quantity
    total_amount = subtotal + delivery_charge

    # Transaction তৈরি
    transaction = Transaction.objects.create(
        buyer=request.user,
        seller=item.user,
        item=item,
        payment_type=payment_type,
        amount=total_amount,
        currency='BDT',
        status='pending',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        gateway_response={
            'delivery_zone': delivery_zone,
            'delivery_charge': delivery_charge,
            'free_delivery': free_delivery,
            'quantity': quantity,
            'unit_price': float(unit_price),
            'subtotal': float(subtotal),
        }
    )

    # Order তৈরি
    order = Order.objects.create(
        buyer=request.user,
        item=item,
        transaction=transaction,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        delivery_name=delivery_name,
        delivery_phone=delivery_phone,
        delivery_address=delivery_address,
        status='pending_payment',
        notes=f"Zone: {'Inside Dhaka' if delivery_zone == 'dhaka' else 'Outside Dhaka'} | Delivery: ৳{delivery_charge} | {notes}".strip(' |'),
    )

    # Payment type অনুযায়ী redirect
    if payment_type == 'sslcommerz':
        return redirect('payment:sslcommerz_init', transaction_id=transaction.transaction_id)
    elif payment_type == 'cod':
        return redirect('payment:cod_confirm', transaction_id=transaction.transaction_id)
    elif payment_type in ['bkash', 'nagad', 'rocket']:
        return redirect('payment:mobile_banking', transaction_id=transaction.transaction_id)
    elif payment_type in ['visa', 'mastercard']:
        return redirect('payment:sslcommerz_init', transaction_id=transaction.transaction_id)
    else:
        messages.error(request, "Invalid payment method.")
        return redirect('payment:checkout', item_pk=item_pk)


# ── SSLCommerz Payment ──
@login_required
def sslcommerz_init(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
        status='pending'
    )

    try:
        from sslcommerz_lib import SSLCOMMERZ

        settings_ssl = {
            'store_id': settings.SSLCOMMERZ_STORE_ID,
            'store_pass': settings.SSLCOMMERZ_STORE_PASSWORD,
            'issandbox': settings.SSLCOMMERZ_SANDBOX,
        }

        sslcz = SSLCOMMERZ(settings_ssl)

        post_body = {
            'total_amount': str(transaction.amount),
            'currency': 'BDT',
            'tran_id': str(transaction.transaction_id),
            'success_url': request.build_absolute_uri(f'/payment/sslcommerz/success/{transaction.transaction_id}/'),
            'fail_url': request.build_absolute_uri(f'/payment/sslcommerz/fail/{transaction.transaction_id}/'),
            'cancel_url': request.build_absolute_uri(f'/payment/sslcommerz/cancel/{transaction.transaction_id}/'),
            'ipn_url': request.build_absolute_uri('/payment/sslcommerz/ipn/'),
            'cus_name': request.user.full_name or request.user.username,
            'cus_email': request.user.email,
            'cus_phone': request.user.phone or '01700000000',
            'cus_add1': transaction.order.delivery_address,
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            'shipping_method': 'YES',
            'product_name': transaction.item.name,
            'product_category': transaction.item.category.name,
            'product_profile': 'general',
            'ship_name': transaction.order.delivery_name,
            'ship_add1': transaction.order.delivery_address,
            'ship_city': 'Dhaka',
            'ship_country': 'Bangladesh',
        }

        response = sslcz.createSession(post_body)

        if response.get('status') == 'SUCCESS':
            transaction.gateway_response = response
            transaction.status = 'processing'
            transaction.save()
            return redirect(response['GatewayPageURL'])
        else:
            messages.error(request, "Payment gateway error. Please try again.")
            return redirect('payment:checkout', item_pk=transaction.item.pk)

    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('payment:checkout', item_pk=transaction.item.pk)


# ── SSLCommerz Success ──
@csrf_exempt
def sslcommerz_success(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)

    if request.method == 'POST':
        val_id = request.POST.get('val_id')
        status = request.POST.get('status')
        amount_received = request.POST.get('amount')

        if status == 'VALID' and val_id:
            try:
                from sslcommerz_lib import SSLCOMMERZ

                ssl_settings = {
                    'store_id': settings.SSLCOMMERZ_STORE_ID,
                    'store_pass': settings.SSLCOMMERZ_STORE_PASSWORD,
                    'issandbox': settings.SSLCOMMERZ_SANDBOX,
                }
                sslcz = SSLCOMMERZ(ssl_settings)

                # ✅ Server-side validation — gateway তে সরাসরি query
                validation = sslcz.hash_validate_ipn(dict(request.POST))

                if validation.get('status') == 'VALID':
                    # ✅ Amount মিলিয়ে দেখো — client data বিশ্বাস করো না
                    validated_amount = float(validation.get('amount', 0))
                    expected_amount = float(transaction.amount)

                    if abs(validated_amount - expected_amount) > 0.01:
                        # Amount mismatch — fraud attempt!
                        transaction.status = 'failed'
                        transaction.gateway_response = {
                            'error': 'Amount mismatch',
                            'expected': expected_amount,
                            'received': validated_amount,
                        }
                        transaction.save()
                        messages.error(request, "Payment verification failed — amount mismatch.")
                        return redirect('payment:failed', transaction_id=transaction_id)

                    # ✅ সব ঠিক আছে — complete করো
                    transaction.status = 'completed'
                    transaction.gateway_transaction_id = val_id
                    transaction.completed_at = timezone.now()
                    transaction.gateway_response = dict(request.POST)
                    transaction.save()

                    order = transaction.order
                    order.status = 'payment_confirmed'
                    order.save()

                    # Item sold mark
                    item = transaction.item
                    item.is_sold = True
                    item.status = 'sold'
                    item.save()

                    # Seller কে notification পাঠাও
                    from core.models import Notification
                    Notification.objects.create(
                        user=item.user,
                        title="Item Sold! 🎉",
                        message=f"Your item '{item.name}' has been sold for ৳{transaction.amount}",
                        notification_type='sale',
                        link=f"/items/{item.id}/",
                    )

                    messages.success(request, "Payment successful! 🎉")
                    return redirect('payment:success', transaction_id=transaction_id)

                else:
                    transaction.status = 'failed'
                    transaction.save()
                    messages.error(request, "Payment validation failed.")
                    return redirect('payment:failed', transaction_id=transaction_id)

            except Exception as e:
                transaction.status = 'failed'
                transaction.save()
                messages.error(request, f"Payment error: {str(e)}")
                return redirect('payment:failed', transaction_id=transaction_id)

        else:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, "Payment failed.")
            return redirect('payment:failed', transaction_id=transaction_id)

    return redirect('payment:success', transaction_id=transaction_id)


# ── SSLCommerz Fail ──
@csrf_exempt
def sslcommerz_fail(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    transaction.status = 'failed'
    transaction.save()
    messages.error(request, "Payment failed. Please try again.")
    return redirect('payment:failed', transaction_id=transaction_id)


# ── SSLCommerz Cancel ──
@csrf_exempt
def sslcommerz_cancel(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    transaction.status = 'cancelled'
    transaction.save()
    messages.warning(request, "Payment cancelled.")
    return redirect('payment:checkout', item_pk=transaction.item.pk)


# ── SSLCommerz IPN ──
@csrf_exempt
@require_POST
def sslcommerz_ipn(request):
    """Instant Payment Notification — gateway থেকে server-to-server notification"""
    try:
        tran_id = request.POST.get('tran_id')
        status = request.POST.get('status')
        val_id = request.POST.get('val_id')

        if tran_id and status == 'VALID':
            transaction = Transaction.objects.get(transaction_id=tran_id)
            if transaction.status != 'completed':
                transaction.status = 'completed'
                transaction.gateway_transaction_id = val_id
                transaction.completed_at = timezone.now()
                transaction.save()

        return HttpResponse("OK")
    except Exception:
        return HttpResponse("ERROR", status=400)


# ── Mobile Banking (bKash/Nagad/Rocket) ──
@login_required
def mobile_banking(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
        status='pending'
    )

    MOBILE_NUMBERS = {
        'bkash': settings.BKASH_MERCHANT_NUMBER,
        'nagad': settings.NAGAD_MERCHANT_NUMBER,
        'rocket': settings.ROCKET_MERCHANT_NUMBER,
    }

    merchant_number = MOBILE_NUMBERS.get(transaction.payment_type, '')

    if request.method == 'POST':
        sender_number = request.POST.get('sender_number', '').strip()
        reference_id = request.POST.get('reference_id', '').strip()

        if not sender_number or not reference_id:
            messages.error(request, "Please provide sender number and reference ID.")
            return render(request, 'payment/mobile_banking.html', {
                'transaction': transaction,
                'merchant_number': merchant_number,
            })

        # Transaction update
        transaction.gateway_transaction_id = reference_id
        transaction.status = 'processing'
        transaction.gateway_response = {
            'sender_number': sender_number[-4:],  # শুধু last 4 digits store
            'reference_id': reference_id,
        }
        transaction.save()

        # Admin verification pending
        order = transaction.order
        order.status = 'pending_payment'
        order.notes = f"Awaiting {transaction.get_payment_type_display()} verification. Ref: {reference_id}"
        order.save()

        messages.success(request, f"Payment submitted! We'll verify your {transaction.get_payment_type_display()} payment within 1 hour.")
        return redirect('payment:pending', transaction_id=transaction_id)

    return render(request, 'payment/mobile_banking.html', {
        'transaction': transaction,
        'merchant_number': merchant_number,
    })


# ── COD Confirm ──
@login_required
def cod_confirm(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
        status='pending'
    )

    if request.method == 'POST':
        transaction.status = 'processing'
        transaction.save()

        order = transaction.order
        order.status = 'payment_confirmed'
        order.save()

        messages.success(request, "Order placed! Pay on delivery. 🚚")
        return redirect('payment:success', transaction_id=transaction_id)

    return render(request, 'payment/cod_confirm.html', {
        'transaction': transaction,
    })


# ── Success Page ──
@login_required
def success(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
    )
    return render(request, 'payment/success.html', {
        'transaction': transaction,
        'order': transaction.order,
    })


# ── Failed Page ──
@login_required
def failed(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
    )
    return render(request, 'payment/failed.html', {
        'transaction': transaction,
    })


# ── Pending Page ──
@login_required
def pending(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        transaction_id=transaction_id,
        buyer=request.user,
    )
    return render(request, 'payment/pending.html', {
        'transaction': transaction,
    })


# ── Save Payment Method ──
@login_required
@require_POST
def save_payment_method(request):
    method_type = request.POST.get('method_type')
    
    if method_type in ['bkash', 'nagad', 'rocket']:
        phone = request.POST.get('phone', '').strip()
        if len(phone) < 4:
            return JsonResponse({'error': 'Invalid phone number'}, status=400)
        
        # শুধু masked version store করো
        masked = phone[:2] + '****' + phone[-4:]
        
        PaymentMethod.objects.create(
            user=request.user,
            method_type=method_type,
            phone_last4=phone[-4:],
            phone_display=masked,
        )

    elif method_type in ['visa', 'mastercard']:
        card_number = request.POST.get('card_number', '').replace(' ', '')
        card_expiry = request.POST.get('card_expiry', '').strip()
        card_holder = request.POST.get('card_holder', '').strip()

        if len(card_number) < 4:
            return JsonResponse({'error': 'Invalid card number'}, status=400)

        # শুধু last 4 digits store করো — full card number কখনো store করো না
        PaymentMethod.objects.create(
            user=request.user,
            method_type=method_type,
            card_last4=card_number[-4:],
            card_brand=method_type.capitalize(),
            card_expiry=card_expiry,
            card_holder_name=card_holder,
        )

    messages.success(request, "Payment method saved!")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ── Delete Payment Method ──
@login_required
def delete_payment_method(request, pk):
    method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    method.is_active = False
    method.save()
    messages.success(request, "Payment method removed.")
    return redirect(request.META.get('HTTP_REFERER', '/'))




# ── Steadfast Integration ──
def create_steadfast_order(order):
    """Steadfast এ consignment তৈরি করো"""
    try:
        response = http_requests.post(
            'https://portal.steadfast.com.bd/api/v1/create_order',
            headers={
                'Api-Key': settings.STEADFAST_API_KEY,
                'Secret-Key': settings.STEADFAST_SECRET_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'invoice': str(order.order_number)[:8].upper(),
                'recipient_name': order.delivery_name,
                'recipient_phone': order.delivery_phone,
                'recipient_address': order.delivery_address,
                'cod_amount': float(order.total_amount) if order.transaction.payment_type == 'cod' else 0,
                'note': order.notes or '',
            },
            timeout=10
        )
        data = response.json()
        if data.get('status') == 200:
            order.steadfast_consignment_id = data['consignment']['consignment_id']
            order.steadfast_tracking_code = data['consignment']['tracking_code']
            order.tracking_url = f"https://steadfast.com.bd/t/{data['consignment']['tracking_code']}"
            order.add_tracking_event('processing', 'Order submitted to Steadfast Courier')
            order.save()
            return True
    except Exception as e:
        print(f"Steadfast error: {e}")
    return False


@login_required
def track_order(request, order_number):
    """Real-time order tracking page"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
    )

    # Buyer, seller অথবা admin দেখতে পারবে
    if not (request.user == order.buyer or
            request.user == order.item.user or
            request.user.is_staff):
        messages.error(request, "You don't have access to this order.")
        return redirect('core:index')

    # Steadfast থেকে live tracking update নাও
    if order.steadfast_tracking_code:
        try:
            response = http_requests.get(
                f'https://portal.steadfast.com.bd/api/v1/status/by_tracking_id/{order.steadfast_tracking_code}',
                headers={
                    'Api-Key': settings.STEADFAST_API_KEY,
                    'Secret-Key': settings.STEADFAST_SECRET_KEY,
                },
                timeout=5
            )
            data = response.json()
            if data.get('status') == 200:
                sf_status = data.get('delivery_status', '')
                # Status map করো
                status_map = {
                    'in_review': 'processing',
                    'partially_dispatched': 'picked_up',
                    'dispatched': 'in_transit',
                    'partially_delivered': 'out_for_delivery',
                    'delivered': 'delivered',
                    'partial_return': 'returned',
                    'returned': 'returned',
                }
                new_status = status_map.get(sf_status)
                if new_status and order.status != new_status:
                    order.status = new_status
                    order.add_tracking_event(new_status, f'Status updated: {sf_status}')
                    if new_status == 'delivered':
                        from django.utils import timezone
                        order.delivered_at = timezone.now()
                        order.save()
        except Exception:
            pass

    return render(request, 'payment/tracking.html', {
        'order': order,
    })