from django.db import models
from django.conf import settings
from item.models import Item
import uuid


class PaymentMethod(models.Model):
    """User এর saved payment methods"""

    METHOD_TYPES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('visa', 'Visa Card'),
        ('mastercard', 'Mastercard'),
        ('sslcommerz', 'SSLCommerz'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='payment_methods',
        on_delete=models.CASCADE
    )
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)

    # Mobile banking — শুধু last 4 digits store করবো
    phone_last4 = models.CharField(max_length=4, blank=True, null=True)
    phone_display = models.CharField(max_length=20, blank=True, null=True)

    # Card
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=20, blank=True, null=True)
    card_expiry = models.CharField(max_length=7, blank=True, null=True)
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-is_default', '-created_at')

    def __str__(self):
        return f"{self.user.username} — {self.get_method_type_display()}"

    def get_display_name(self):
        if self.method_type in ['bkash', 'nagad', 'rocket']:
            return f"{self.get_method_type_display()} ({self.phone_display})"
        elif self.method_type in ['visa', 'mastercard']:
            return f"{self.card_brand} •••• {self.card_last4}"
        return self.get_method_type_display()


class Transaction(models.Model):
    """প্রতিটা payment transaction এর record"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_TYPES = [
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('visa', 'Visa Card'),
        ('mastercard', 'Mastercard'),
        ('sslcommerz', 'SSLCommerz'),
        ('cod', 'Cash on Delivery'),
    ]

    transaction_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )
    gateway_transaction_id = models.CharField(
        max_length=200,
        blank=True, null=True,
        db_index=True
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='payment_transactions',
        on_delete=models.PROTECT
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_transactions',
        on_delete=models.PROTECT
    )
    item = models.ForeignKey(
        Item,
        related_name='transactions',
        on_delete=models.PROTECT
    )

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    gateway_response = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.transaction_id} — {self.amount} BDT — {self.status}"


class Order(models.Model):
    """Purchase order"""

    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('processing', 'Processing'),
        ('picked_up', 'Picked Up by Courier'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('returned', 'Returned'),
    ]

    ZONE_CHOICES = [
        ('dhaka', 'Inside Dhaka'),
        ('outside', 'Outside Dhaka'),
    ]

    order_number = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='payment_orders',
        on_delete=models.PROTECT
    )
    item = models.ForeignKey(
        Item,
        related_name='payment_item_orders',
        on_delete=models.PROTECT
    )
    transaction = models.OneToOneField(
        Transaction,
        related_name='order',
        on_delete=models.PROTECT,
        blank=True, null=True
    )

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=80)
    free_delivery = models.BooleanField(default=False)
    delivery_zone = models.CharField(max_length=20, choices=ZONE_CHOICES, default='dhaka')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_address = models.TextField()
    delivery_phone = models.CharField(max_length=20)
    delivery_name = models.CharField(max_length=100)
    delivery_city = models.CharField(max_length=100, blank=True, null=True)

    # Steadfast tracking
    steadfast_consignment_id = models.CharField(max_length=100, blank=True, null=True)
    steadfast_tracking_code = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tracking_url = models.URLField(blank=True, null=True)

    # Tracking history (JSON)
    tracking_history = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_payment',
        db_index=True
    )

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order #{str(self.order_number)[:8]} — {self.item.name}"

    def get_delivery_charge_display(self):
        if self.free_delivery:
            return "Free (Seller Sponsored)"
        return f"৳{self.delivery_charge}"

    def add_tracking_event(self, status, message, location=''):
        """Tracking history তে নতুন event যোগ করো"""
        from django.utils import timezone
        if not isinstance(self.tracking_history, list):
            self.tracking_history = []
        self.tracking_history.append({
            'status': status,
            'message': message,
            'location': location,
            'timestamp': timezone.now().isoformat(),
        })
        self.save()