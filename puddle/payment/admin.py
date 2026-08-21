from django.contrib import admin
from .models import PaymentMethod, Transaction, Order, Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit', 'valid_until')
    list_filter = ('discount_type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'item', 'total_amount', 'status', 'delivery_zone', 'created_at')
    list_filter = ('status', 'delivery_zone')
    search_fields = ('order_number', 'buyer__username', 'item__name')
    list_editable = ('status',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'buyer', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_type', 'status')
    search_fields = ('transaction_id', 'buyer__username')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'is_default', 'is_active')
    list_filter = ('method_type', 'is_active')