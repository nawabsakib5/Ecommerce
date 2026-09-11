from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q

from cart.models import COMMISSION_RATE, Sale
from item.models import Item

User = get_user_model()


def build_admin_dashboard_data():
    """
    ✅ N+1 Query fix — আগে ১০০ user হলে ৪০০+ query হতো
    এখন মাত্র ৫টা query দিয়ে সব data নেওয়া হচ্ছে
    """

    # ── Query 1: সব user একবারে ──
    users = list(User.objects.order_by('username'))
    user_ids = [u.pk for u in users]

    # ── Query 2: সব available items একবারে ──
    # user_id দিয়ে group করার জন্য Python dict বানাই
    all_available_items = (
        Item.objects
        .filter(user_id__in=user_ids, is_sold=False)
        .select_related('category')
        .order_by('-created_at')
    )
    # user_id → [items] map
    available_map = {}
    for item in all_available_items:
        available_map.setdefault(item.user_id, []).append(item)

    # ── Query 3: সব sold items count + revenue একবারে ──
    sold_agg = (
        Item.objects
        .filter(user_id__in=user_ids, is_sold=True)
        .values('user_id')
        .annotate(
            sold_count=Count('id'),
            revenue=Sum('original_price'),
        )
    )
    # user_id → {sold_count, revenue} map
    sold_map = {
        row['user_id']: {
            'sold_count': row['sold_count'] or 0,
            'revenue': round(row['revenue'] or 0, 2),
        }
        for row in sold_agg
    }

    # ── Query 4: Sale model থেকে সব seller revenue একবারে ──
    sale_agg = (
        Sale.objects
        .filter(seller_id__in=user_ids)
        .values('seller_id')
        .annotate(
            revenue=Sum('total_amount'),
            commission=Sum('commission_amount'),
            qty=Sum('quantity'),
        )
    )
    # seller_id → {revenue, commission, qty} map
    sale_map = {
        row['seller_id']: {
            'revenue': round(row['revenue'] or 0, 2),
            'commission': round(row['commission'] or 0, 2),
            'sold_count': row['qty'] or 0,
        }
        for row in sale_agg
    }

    # ── Python-এ user_rows build করো — আর কোনো DB query নেই ──
    user_rows = []
    grand_sales = 0.0
    grand_commission = 0.0
    grand_sold_qty = 0
    grand_available = 0

    for user in users:
        available_items = available_map.get(user.pk, [])
        available_count = len(available_items)

        # Sale model-এ data আছে কিনা দেখো — থাকলে সেটা বেশি accurate
        if user.pk in sale_map:
            s = sale_map[user.pk]
            revenue = s['revenue']
            commission = s['commission']
            sold_count = s['sold_count']
        elif user.pk in sold_map:
            # Sale model-এ নেই — Item model থেকে estimate করো
            s = sold_map[user.pk]
            revenue = s['revenue']
            commission = round(revenue * COMMISSION_RATE, 2)
            sold_count = s['sold_count']
        else:
            revenue = 0.0
            commission = 0.0
            sold_count = 0

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

    # ── Query 5: Recent sales ──
    recent_sales = (
        Sale.objects
        .select_related('item', 'seller', 'buyer', 'item__category')
        .order_by('-sold_at')[:20]
    )

    return {
        'user_rows': user_rows,
        'total_users': len(users),
        'grand_sales': round(grand_sales, 2),
        'grand_commission': round(grand_commission, 2),
        'grand_sold_qty': grand_sold_qty,
        'grand_available': grand_available,
        'commission_rate_pct': int(COMMISSION_RATE * 100),
        'recent_sales': recent_sales,
    }