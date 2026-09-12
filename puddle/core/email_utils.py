from django.core.mail import send_mail
from django.conf import settings


# ── Common Email Wrapper ──
def _send(subject, recipient_list, html_message):
    """সব email এই function দিয়ে পাঠানো হবে"""
    try:
        send_mail(
            subject=subject,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception:
        pass


# ── Common HTML Components ──
def _header():
    return """
    <div style="font-family:'Plus Jakarta Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f7f4;padding:32px;border-radius:20px;">
        <div style="text-align:center;margin-bottom:24px;">
            <div style="display:inline-block;background:#0b0f19;border-radius:14px;padding:10px 24px;">
                <h1 style="font-size:22px;color:white;margin:0;letter-spacing:0.05em;">CADO <span style="color:#D4AF37;">Fashion</span></h1>
            </div>
        </div>
    """

def _footer():
    return """
        <p style="text-align:center;color:#aaa;font-size:11px;margin-top:24px;">
            © 2026 CADO Fashion. All rights reserved.<br>
            <a href="https://cadobd.com" style="color:#9A7432;text-decoration:none;">cadobd.com</a>
        </p>
    </div>
    """

def _card(content, border_color="#e8e5e0"):
    return f"""
    <div style="background:#fff;border-radius:14px;padding:28px;border:1.5px solid {border_color};margin-bottom:8px;">
        {content}
    </div>
    """

def _info_row(label, value):
    return f'<p style="margin:6px 0;font-size:13px;color:#555;"><strong style="color:#1a1a2e;">{label}:</strong> {value}</p>'

def _info_box(*rows):
    content = "".join(rows)
    return f'<div style="background:#f8f7f4;border-radius:10px;padding:16px;margin:16px 0;">{content}</div>'

def _btn(text, url, color="#9A7432"):
    return f"""
    <div style="text-align:center;margin-top:20px;">
        <a href="{url}" style="display:inline-block;background:{color};color:white;padding:12px 32px;border-radius:12px;text-decoration:none;font-weight:700;font-size:14px;letter-spacing:0.03em;">{text}</a>
    </div>
    """


# ══════════════════════════════════════════
# 1. Order Confirmation — Buyer
# ══════════════════════════════════════════
def send_order_confirmation(order):
    """Order confirm হলে buyer কে email"""
    payment_type = order.transaction.get_payment_type_display() if hasattr(order, 'transaction') and order.transaction else "N/A"

    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">🎉 Order Confirmed!</h2>
        <p style="color:#555;font-size:14px;margin-bottom:16px;">
            Hi <strong>{order.delivery_name}</strong>, your order has been placed successfully.
            We'll notify you when it's shipped.
        </p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Quantity", f"{order.quantity} pcs"),
            _info_row("Total Amount", f"৳{order.total_amount}"),
            _info_row("Payment Method", payment_type),
            _info_row("Delivery Address", order.delivery_address),
        )}
        <p style="color:#777;font-size:13px;">Estimated delivery: <strong>2–5 business days</strong> via Steadfast Courier.</p>
        {_btn("Track Your Order", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/payment/track/{order.order_number}/")}
    """) + _footer()

    _send(
        subject=f"Order Confirmed #{str(order.order_number)[:8].upper()} — CADO Fashion",
        recipient_list=[order.buyer.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# 2. Order Status Update — Buyer
# ══════════════════════════════════════════
def send_order_status_update(order):
    """Order status update হলে buyer কে email"""
    status_map = {
        'processing':       ('📦 Order Processing',     'Your order is being processed and will be shipped soon.'),
        'picked_up':        ('🚚 Order Picked Up',       'Your order has been picked up by our courier partner Steadfast.'),
        'in_transit':       ('🛣️ Order In Transit',      'Your order is on its way! Track it for live updates.'),
        'out_for_delivery': ('🏃 Out for Delivery',      'Your order is out for delivery today. Please be available to receive it.'),
        'delivered':        ('🎉 Order Delivered!',      'Your order has been delivered successfully. We hope you love it!'),
        'cancelled':        ('❌ Order Cancelled',       'Your order has been cancelled. If you have any questions, please contact us.'),
        'refunded':         ('💰 Refund Processed',      'Your refund has been processed. It may take 3–5 business days to reflect.'),
    }

    info = status_map.get(order.status)
    if not info:
        return

    subject, message = info
    border = "#d1fae5" if order.status == 'delivered' else "#e8e5e0"

    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">{subject}</h2>
        <p style="color:#555;font-size:14px;">Hi <strong>{order.delivery_name}</strong>,</p>
        <p style="color:#555;font-size:14px;margin-bottom:16px;">{message}</p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Status", order.get_status_display()),
        )}
        {_btn("Track Your Order", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/payment/track/{order.order_number}/")}
    """, border_color=border) + _footer()

    _send(
        subject=f"{subject} — CADO Fashion",
        recipient_list=[order.buyer.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# 3. Return Request — Seller
# ══════════════════════════════════════════
def send_return_request_notification(order):
    """Return request হলে seller কে email"""
    html = _header() + _card(f"""
        <h2 style="color:#c84b31;margin-top:0;font-size:20px;">↩️ Return Request Received</h2>
        <p style="color:#555;font-size:14px;">
            A buyer has requested a return for <strong>{order.item.name}</strong>.
            Please review and respond within 48 hours.
        </p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Buyer", order.buyer.username),
            _info_row("Reason", order.return_request.get_reason_display()),
            _info_row("Description", order.return_request.description),
        )}
        {_btn("Review Return Request", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/dashboard/orders/", color="#c84b31")}
    """, border_color="#fecaca") + _footer()

    _send(
        subject=f"↩️ Return Request — {order.item.name} | CADO Fashion",
        recipient_list=[order.item.user.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# ✅ 4. Welcome Email — New Buyer (NEW)
# ══════════════════════════════════════════
def send_welcome_email(user):
    """Signup করলে buyer কে welcome email"""
    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">👋 Welcome to CADO Fashion!</h2>
        <p style="color:#555;font-size:14px;">
            Hi <strong>{user.username}</strong>, we're thrilled to have you on board!
            Discover the latest fashion trends and shop your favorites.
        </p>
        <div style="background:#f8f7f4;border-radius:10px;padding:16px;margin:16px 0;">
            <p style="margin:6px 0;font-size:13px;color:#555;">✅ <strong>Browse</strong> thousands of fashion items</p>
            <p style="margin:6px 0;font-size:13px;color:#555;">✅ <strong>Pay</strong> via bKash, Nagad, COD & more</p>
            <p style="margin:6px 0;font-size:13px;color:#555;">✅ <strong>Track</strong> your orders in real-time</p>
            <p style="margin:6px 0;font-size:13px;color:#555;">✅ <strong>Return</strong> easily if needed</p>
        </div>
        <p style="color:#777;font-size:13px;">
            Your account email: <strong>{user.email}</strong>
        </p>
        {_btn("Start Shopping 🛍️", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else '/'}")}
    """, border_color="#d1fae5") + _footer()

    _send(
        subject="Welcome to CADO Fashion! 🎉",
        recipient_list=[user.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# ✅ 5. New Order Notification — Seller (NEW)
# ══════════════════════════════════════════
def send_new_order_to_seller(order):
    """নতুন order হলে seller কে email notification"""
    payment_type = order.transaction.get_payment_type_display() if hasattr(order, 'transaction') and order.transaction else "N/A"

    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">🛒 New Order Received!</h2>
        <p style="color:#555;font-size:14px;">
            Great news! You have a new order for <strong>{order.item.name}</strong>.
            Please prepare the item for shipment.
        </p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Quantity", f"{order.quantity} pcs"),
            _info_row("Amount", f"৳{order.total_amount}"),
            _info_row("Payment", payment_type),
            _info_row("Buyer", order.buyer.username),
            _info_row("Delivery Address", order.delivery_address),
        )}
        <p style="color:#777;font-size:13px;">Please process this order within <strong>24 hours</strong>.</p>
        {_btn("View Order Dashboard", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/dashboard/orders/")}
    """, border_color="#ddd6fe") + _footer()

    _send(
        subject=f"🛒 New Order — {order.item.name} | CADO Fashion",
        recipient_list=[order.item.user.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# ✅ 6. bKash/Nagad Verify Pending — Admin (NEW)
# ══════════════════════════════════════════
def send_mobile_payment_pending_to_admin(order):
    """bKash/Nagad manual payment submit হলে admin কে email"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # সব admin/staff এর email নাও
    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )
    if not admin_emails:
        return

    payment_type = order.transaction.get_payment_type_display() if hasattr(order, 'transaction') and order.transaction else "Mobile Banking"
    ref_id = order.transaction.gateway_transaction_id if hasattr(order, 'transaction') and order.transaction else "N/A"

    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">⏳ Payment Verification Required</h2>
        <p style="color:#555;font-size:14px;">
            A buyer has submitted a <strong>{payment_type}</strong> payment that needs manual verification.
        </p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Buyer", f"{order.buyer.username} ({order.buyer.email})"),
            _info_row("Payment Method", payment_type),
            _info_row("Reference ID", ref_id),
            _info_row("Amount", f"৳{order.total_amount}"),
        )}
        <p style="color:#c84b31;font-size:13px;font-weight:bold;">
            ⚠️ Please verify this payment in your admin dashboard within 1 hour.
        </p>
        {_btn("Verify Payment Now", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/dashboard/orders/", color="#c84b31")}
    """, border_color="#fde68a") + _footer()

    _send(
        subject=f"⏳ Payment Verification Needed — {payment_type} | CADO Fashion",
        recipient_list=admin_emails,
        html_message=html,
    )


# ══════════════════════════════════════════
# ✅ 7. Return Approved/Rejected — Buyer (NEW)
# ══════════════════════════════════════════
def send_return_decision_to_buyer(order, approved: bool, admin_note: str = ""):
    """Return approve বা reject হলে buyer কে email"""
    if approved:
        subject = "✅ Return Approved — CADO Fashion"
        heading = "✅ Return Request Approved"
        message = "Your return request has been approved. Your refund will be processed within 3–5 business days."
        border = "#d1fae5"
        btn_color = "#059669"
    else:
        subject = "❌ Return Request Rejected — CADO Fashion"
        heading = "❌ Return Request Rejected"
        message = "We're sorry, your return request has been reviewed and could not be approved at this time."
        border = "#fee2e2"
        btn_color = "#c84b31"

    note_html = f'<p style="color:#555;font-size:13px;"><strong>Admin Note:</strong> {admin_note}</p>' if admin_note else ""

    html = _header() + _card(f"""
        <h2 style="color:#1a1a2e;margin-top:0;font-size:20px;">{heading}</h2>
        <p style="color:#555;font-size:14px;">Hi <strong>{order.buyer.username}</strong>,</p>
        <p style="color:#555;font-size:14px;margin-bottom:16px;">{message}</p>
        {_info_box(
            _info_row("Order ID", f"#{str(order.order_number)[:8].upper()}"),
            _info_row("Item", order.item.name),
            _info_row("Decision", "Approved ✅" if approved else "Rejected ❌"),
        )}
        {note_html}
        <p style="color:#777;font-size:13px;">
            If you have any questions, please contact us at
            <a href="mailto:support.cadobd@gmail.com" style="color:#9A7432;">support.cadobd@gmail.com</a>
        </p>
        {_btn("View Orders", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/dashboard/orders/", color=btn_color)}
    """, border_color=border) + _footer()

    _send(
        subject=subject,
        recipient_list=[order.buyer.email],
        html_message=html,
    )


# ══════════════════════════════════════════
# ✅ 8. Low Stock Alert — Admin (NEW)
# ══════════════════════════════════════════
def send_low_stock_alert(item, remaining_stock: int):
    """Stock কম হলে admin কে email alert"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    admin_emails = list(
        User.objects.filter(is_staff=True, is_active=True)
        .values_list('email', flat=True)
    )
    if not admin_emails:
        return

    urgency = "🔴 Critical" if remaining_stock == 0 else "🟡 Low"
    urgency_color = "#dc2626" if remaining_stock == 0 else "#d97706"

    html = _header() + _card(f"""
        <h2 style="color:{urgency_color};margin-top:0;font-size:20px;">{urgency} — Stock Alert</h2>
        <p style="color:#555;font-size:14px;">
            <strong>{item.name}</strong> is {'out of stock' if remaining_stock == 0 else f'running low with only {remaining_stock} unit(s) remaining'}.
        </p>
        {_info_box(
            _info_row("Item", item.name),
            _info_row("Category", item.category.name if item.category else "N/A"),
            _info_row("Seller", item.user.username),
            _info_row("Remaining Stock", str(remaining_stock)),
            _info_row("Price", f"৳{item.original_price}"),
        )}
        <p style="color:{urgency_color};font-size:13px;font-weight:bold;">
            {'⚠️ This item is now out of stock and has been marked as sold.' if remaining_stock == 0 else '⚠️ Please restock this item soon to avoid missed sales.'}
        </p>
        {_btn("View Item", f"{settings.SITE_URL if hasattr(settings,'SITE_URL') else ''}/items/{item.id}/", color=urgency_color)}
    """, border_color="#fde68a") + _footer()

    _send(
        subject=f"{urgency} Stock Alert — {item.name} | CADO Fashion",
        recipient_list=admin_emails,
        html_message=html,
    )