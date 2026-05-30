from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.shortcuts import render, redirect

from item.models import Item, Category
from item.seed_helpers import is_admin_user
from .admin_stats import build_admin_dashboard_data
from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile


@login_required
def index(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('dashboard:admin')
    if request.user.user_type == 'Buyer':
        return redirect('dashboard:buyer')
    return seller_dashboard(request)


@login_required
def seller_dashboard(request):
    from cart.models import Sale
    from core.models import Review
    from conversation.models import Conversation

    profile, _ = Profile.objects.get_or_create(user=request.user)
    items = (
        Item.objects.filter(user=request.user)
        .select_related('category')
        .order_by('-created_at')
    )

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard:index')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    active_items = items.filter(is_sold=False)
    sold_items = items.filter(is_sold=True)
    inventory_value = active_items.aggregate(total=Sum('price'))['total'] or 0

    # Analytics
    sales = Sale.objects.filter(seller=request.user)
    total_revenue = round(sales.aggregate(t=Sum('total_amount'))['t'] or 0, 2)
    total_commission = round(sales.aggregate(t=Sum('commission_amount'))['t'] or 0, 2)
    net_income = round(total_revenue - total_commission, 2)

    # Revenue by category
    revenue_by_cat = []
    for cat in Category.objects.all():
        cat_sales = sales.filter(item__category=cat)
        if cat_sales.exists():
            rev = round(cat_sales.aggregate(t=Sum('total_amount'))['t'] or 0, 2)
            revenue_by_cat.append({'name': cat.name, 'revenue': rev})
    revenue_by_cat = sorted(revenue_by_cat, key=lambda x: x['revenue'], reverse=True)[:8]

    # Top selling items
    top_items = (
        sold_items.annotate(sale_count=Count('sales'))
        .order_by('-sale_count')[:5]
    )

    # Messages count
    message_count = Conversation.objects.filter(members=request.user).count()

    # Low stock
    low_stock = active_items.filter(image='')[:5]

    # Recent sales
    recent_sales = sales.select_related('item', 'buyer').order_by('-sold_at')[:10]

    return render(request, 'dashboard/index.html', {
        'items': items,
        'active_count': active_items.count(),
        'sold_count': sold_items.count(),
        'inventory_value': round(inventory_value, 2),
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'net_income': net_income,
        'revenue_by_cat': revenue_by_cat,
        'top_items': top_items,
        'message_count': message_count,
        'low_stock': low_stock,
        'recent_sales': recent_sales,
    })


@login_required
def buyer_dashboard(request):
    from cart.models import Cart, Order
    from core.models import Wishlist, Review

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard:buyer')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.select_related('item', 'item__category').all()

    orders = Order.objects.filter(
        buyer=request.user
    ).prefetch_related('order_items__item').order_by('-created_at')

    total_spent = round(sum(o.total_amount for o in orders), 2)

    wishlist = Wishlist.objects.filter(
        user=request.user
    ).select_related('item', 'item__category')

    reviews = Review.objects.filter(
        user=request.user
    ).select_related('item')

    wishlist_categories = wishlist.values_list('item__category', flat=True)
    recommended = Item.objects.filter(
        category__in=wishlist_categories,
        is_sold=False
    ).exclude(
        wishlisted_by__user=request.user
    ).select_related('category')[:6]

    return render(request, 'dashboard/buyer.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'cart': cart,
        'cart_items': cart_items,
        'orders': orders,
        'total_spent': total_spent,
        'wishlist': wishlist,
        'reviews': reviews,
        'recommended': recommended,
    })


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    context = build_admin_dashboard_data()
    return render(request, 'dashboard/admin.html', context)