from django.db import models
from django.conf import settings
from item.models import Item
import uuid


class PaymentMethod(models.Model):
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
    phone_last4 = models.CharField(max_length=4, blank=True, null=True)
    phone_display = models.CharField(max_length=20, blank=True, null=True)
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
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('confirmed', 'Order Confirmed (COD)'),
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
    variant = models.ForeignKey(
        'item.ProductVariant',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True, blank=True
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
    steadfast_consignment_id = models.CharField(max_length=100, blank=True, null=True)
    steadfast_tracking_code = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tracking_url = models.URLField(blank=True, null=True)
    tracking_history = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending_payment',
        db_index=True
    )
    stock_deducted = models.BooleanField(default=False)
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

    def confirm_payment(self):
        from django.db import transaction as db_transaction
        from item.models import Item, ProductVariant

        if self.stock_deducted:
            return True

        with db_transaction.atomic():
            if self.variant_id:
                variant = ProductVariant.objects.select_for_update().get(pk=self.variant_id)
                if variant.stock < self.quantity:
                    return False
                variant.stock -= self.quantity
                variant.save(update_fields=['stock'])
            else:
                item = Item.objects.select_for_update().get(pk=self.item_id)
                if item.stock_count < self.quantity:
                    return False
                item.stock_count -= self.quantity
                item.save(update_fields=['stock_count'])

            self.stock_deducted = True
            self.status = 'payment_confirmed'
            self.save(update_fields=['stock_deducted', 'status'])

        self.item.sync_status_from_stock()
        return True

    def restore_stock(self):
        from django.db import transaction as db_transaction
        from item.models import Item, ProductVariant

        if not self.stock_deducted:
            return

        with db_transaction.atomic():
            if self.variant_id:
                variant = ProductVariant.objects.select_for_update().get(pk=self.variant_id)
                variant.stock += self.quantity
                variant.save(update_fields=['stock'])
            else:
                item = Item.objects.select_for_update().get(pk=self.item_id)
                item.stock_count += self.quantity
                item.save(update_fields=['stock_count'])

            self.stock_deducted = False
            self.save(update_fields=['stock_deducted'])

        self.item.sync_status_from_stock()


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percent', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('free_delivery', 'Free Delivery'),
    ]

    code = models.CharField(max_length=20, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_coupons',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.code} — {self.get_discount_type_display()}"

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            self.used_count < self.usage_limit
        )

    def get_discount_amount(self, order_amount):
        if self.discount_type == 'percent':
            discount = order_amount * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return round(discount, 2)
        elif self.discount_type == 'fixed':
            return min(self.discount_value, order_amount)
        return 0


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='usages', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coupon_usages', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='coupon_usage', on_delete=models.CASCADE, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'user')

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code}"