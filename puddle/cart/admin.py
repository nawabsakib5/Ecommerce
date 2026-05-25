from django.contrib import admin

from .models import Cart, CartItem, Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'seller',
        'buyer',
        'quantity',
        'total_amount',
        'commission_amount',
        'sold_at',
    )
    list_filter = ('sold_at', 'seller')
    search_fields = ('item__name', 'seller__username', 'buyer__username')


admin.site.register(Cart)
admin.site.register(CartItem)
