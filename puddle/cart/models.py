from django.db import models
from django.conf import settings
from item.models import Item


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='cart',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s cart"

    def get_total(self):
        return round(sum(
            item.get_subtotal() for item in self.cart_items.all()
        ), 2)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='cart_items',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item,
        related_name='cart_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

    def get_subtotal(self):
        return round(self.quantity * self.item.price, 2)

    class Meta:
        unique_together = ('cart', 'item')