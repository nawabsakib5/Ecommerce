from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation(order):
    """Order confirm হলে buyer কে email"""
    try:
        send_mail(
            subject=f"Order Confirmed #{str(order.order_number)[:8].upper()} — CADO Fashion",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer.email],
            html_message=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f7f4;padding:32px;border-radius:16px;">
                <div style="text-align:center;margin-bottom:24px;">
                    <h1 style="font-size:28px;color:#1a1a2e;margin:0;">CADO <span style="color:#9A7432;">Fashion</span></h1>
                </div>
                <div style="background:#fff;border-radius:12px;padding:24px;border:1.5px solid #e8e5e0;">
                    <h2 style="color:#1a1a2e;margin-top:0;">🎉 Order Confirmed!</h2>
                    <p style="color:#555;font-size:14px;">Hi <strong>{order.delivery_name}</strong>, your order has been confirmed.</p>
                    <div style="background:#f8f7f4;border-radius:10px;padding:16px;margin:16px 0;">
                        <p style="margin:4px 0;font-size:13px;"><strong>Order ID:</strong> #{str(order.order_number)[:8].upper()}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Item:</strong> {order.item.name}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Quantity:</strong> {order.quantity} pcs</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Total:</strong> ৳{order.total_amount}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Delivery To:</strong> {order.delivery_address}</p>
                    </div>
                    <p style="color:#555;font-size:13px;">We'll notify you when your order is shipped. Estimated delivery: 2-5 business days.</p>
                </div>
                <p style="text-align:center;color:#aaa;font-size:11px;margin-top:20px;">© 2026 CADO Fashion. All rights reserved.</p>
            </div>
            """,
            fail_silently=True,
        )
    except Exception:
        pass


def send_order_status_update(order):
    """Order status update হলে buyer কে email"""
    status_messages = {
        'processing': ('📦 Order Processing', 'Your order is being processed and will be shipped soon.'),
        'picked_up': ('🚚 Order Picked Up', 'Your order has been picked up by our courier partner.'),
        'in_transit': ('🛣️ Order In Transit', 'Your order is on its way to you!'),
        'out_for_delivery': ('🏃 Out for Delivery', 'Your order is out for delivery today. Please be available.'),
        'delivered': ('🎉 Order Delivered', 'Your order has been delivered. We hope you love it!'),
        'cancelled': ('❌ Order Cancelled', 'Your order has been cancelled.'),
        'refunded': ('💰 Refund Processed', 'Your refund has been processed successfully.'),
    }

    status_info = status_messages.get(order.status)
    if not status_info:
        return

    subject, message = status_info

    try:
        send_mail(
            subject=f"{subject} — CADO Fashion",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.buyer.email],
            html_message=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f7f4;padding:32px;border-radius:16px;">
                <div style="text-align:center;margin-bottom:24px;">
                    <h1 style="font-size:28px;color:#1a1a2e;margin:0;">CADO <span style="color:#9A7432;">Fashion</span></h1>
                </div>
                <div style="background:#fff;border-radius:12px;padding:24px;border:1.5px solid #e8e5e0;">
                    <h2 style="color:#1a1a2e;margin-top:0;">{subject}</h2>
                    <p style="color:#555;font-size:14px;">Hi <strong>{order.delivery_name}</strong>,</p>
                    <p style="color:#555;font-size:14px;">{message}</p>
                    <div style="background:#f8f7f4;border-radius:10px;padding:16px;margin:16px 0;">
                        <p style="margin:4px 0;font-size:13px;"><strong>Order ID:</strong> #{str(order.order_number)[:8].upper()}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Item:</strong> {order.item.name}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Status:</strong> {order.get_status_display()}</p>
                    </div>
                </div>
                <p style="text-align:center;color:#aaa;font-size:11px;margin-top:20px;">© 2026 CADO Fashion. All rights reserved.</p>
            </div>
            """,
            fail_silently=True,
        )
    except Exception:
        pass


def send_return_request_notification(order):
    """Return request হলে seller কে email"""
    try:
        send_mail(
            subject=f"Return Request — {order.item.name} | CADO Fashion",
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.item.user.email],
            html_message=f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f7f4;padding:32px;border-radius:16px;">
                <div style="background:#fff;border-radius:12px;padding:24px;border:1.5px solid #e8e5e0;">
                    <h2 style="color:#c84b31;margin-top:0;">↩️ Return Request Received</h2>
                    <p style="color:#555;font-size:14px;">A buyer has requested a return for <strong>{order.item.name}</strong>.</p>
                    <div style="background:#f8f7f4;border-radius:10px;padding:16px;margin:16px 0;">
                        <p style="margin:4px 0;font-size:13px;"><strong>Order ID:</strong> #{str(order.order_number)[:8].upper()}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Reason:</strong> {order.return_request.get_reason_display()}</p>
                        <p style="margin:4px 0;font-size:13px;"><strong>Description:</strong> {order.return_request.description}</p>
                    </div>
                    <p style="color:#555;font-size:13px;">Please login to your dashboard to review and process this return request.</p>
                </div>
                <p style="text-align:center;color:#aaa;font-size:11px;margin-top:20px;">© 2026 CADO Fashion. All rights reserved.</p>
            </div>
            """,
            fail_silently=True,
        )
    except Exception:
        pass