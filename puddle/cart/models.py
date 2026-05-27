from django.conf import settings
from django.db import models

from item.models import Item

COMMISSION_RATE = 0.02


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='cart',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    def get_total(self):
        return round(sum(
            item.get_subtotal() for item in self.cart_items.all()
        ), 2)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

    def get_subtotal(self):
        return round(self.quantity * self.item.price, 2)

    class Meta:
        unique_together = ('cart', 'item')


class Sale(models.Model):
    item = models.ForeignKey(Item, related_name='sales', on_delete=models.CASCADE)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sales_as_seller', on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='purchases', on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.FloatField()
    total_amount = models.FloatField()
    commission_rate = models.FloatField(default=COMMISSION_RATE)
    commission_amount = models.FloatField()
    sold_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-sold_at',)

    def __str__(self):
        return f'{self.item.name} — ${self.total_amount}'

    @staticmethod
    def calc_commission(total_amount, rate=COMMISSION_RATE):
        return round(total_amount * rate, 2)


# ✅ Order model — buyer এর purchase history
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE
    )
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order #{self.id} — {self.buyer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField()
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sold_order_items',
        on_delete=models.CASCADE
    )

    def get_subtotal(self):
        return round(self.quantity * self.price, 2)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"