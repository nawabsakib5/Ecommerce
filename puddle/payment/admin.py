from django.contrib import admin
from django.contrib import messages
from .models import PaymentMethod, Transaction, Order, Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit', 'valid_until')
    list_filter = ('discount_type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'item', 'total_amount', 'status', 'stock_deducted', 'delivery_zone', 'created_at')
    list_filter = ('status', 'stock_deducted', 'delivery_zone')
    search_fields = ('order_number', 'buyer__username', 'item__name')
    list_editable = ('status',)
    actions = ['verify_and_confirm_payment', 'cancel_and_restore_stock']

    def verify_and_confirm_payment(self, request, queryset):
        success, failed = 0, 0
        for order in queryset:
            if order.confirm_payment():
                success += 1
            else:
                failed += 1
        self.message_user(
            request,
            f"{success} টা confirm হয়েছে, {failed} টা stock না থাকায় fail।",
            messages.SUCCESS
        )
    verify_and_confirm_payment.short_description = "✅ Verify & Confirm Payment (deduct stock)"

    def cancel_and_restore_stock(self, request, queryset):
        for order in queryset:
            order.restore_stock()
            order.status = 'cancelled'
            order.save(update_fields=['status'])
        self.message_user(
            request,
            "Order cancel করা হয়েছে, stock ফেরত দেওয়া হয়েছে।",
            messages.SUCCESS
        )
    cancel_and_restore_stock.short_description = "❌ Cancel Order & Restore Stock"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'buyer', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('payment_type', 'status')
    search_fields = ('transaction_id', 'buyer__username')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'is_default', 'is_active')
    list_filter = ('method_type', 'is_active')