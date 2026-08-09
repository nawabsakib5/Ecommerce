from django.contrib.auth import get_user_model
from django.db.models import Sum

from cart.models import COMMISSION_RATE, Sale
from item.models import Item

User = get_user_model()


def build_admin_dashboard_data():
    users = User.objects.order_by('username')
    user_rows = []

    grand_sales = 0.0
    grand_commission = 0.0
    grand_sold_qty = 0
    grand_available = 0

    for user in users:
        available_items = list(
            Item.objects.filter(user=user, is_sold=False)
            .select_related('category')
            .order_by('-created_at')
        )
        sales_qs = Sale.objects.filter(seller=user)

        if sales_qs.exists():
            agg = sales_qs.aggregate(
                revenue=Sum('total_amount'),
                commission=Sum('commission_amount'),
                qty=Sum('quantity'),
            )
            sold_count = agg['qty'] or 0
            revenue = round(agg['revenue'] or 0, 2)
            commission = round(agg['commission'] or 0, 2)
        else:
            sold_items = Item.objects.filter(user=user, is_sold=True)
            sold_count = sold_items.count()
            revenue = round(
            sold_items.aggregate(t=Sum('original_price'))['t'] or 0, 2
            )
            commission = round(revenue * COMMISSION_RATE, 2)

        available_count = len(available_items)
        grand_sales += revenue
        grand_commission += commission
        grand_sold_qty += sold_count
        grand_available += available_count

        user_rows.append({
            'user': user,
            'available_items': available_items,
            'available_count': available_count,
            'sold_count': sold_count,
            'revenue': revenue,
            'commission': commission,
        })

    recent_sales = (
        Sale.objects.select_related('item', 'seller', 'buyer', 'item__category')
        .order_by('-sold_at')[:20]
    )

    return {
        'user_rows': user_rows,
        'total_users': users.count(),
        'grand_sales': round(grand_sales, 2),
        'grand_commission': round(grand_commission, 2),
        'grand_sold_qty': grand_sold_qty,
        'grand_available': grand_available,
        'commission_rate_pct': int(COMMISSION_RATE * 100),
        'recent_sales': recent_sales,
    }
