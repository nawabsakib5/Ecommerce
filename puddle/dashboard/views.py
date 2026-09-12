from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.views.decorators.http import require_POST

from item.models import Item, Category
from dashboard.models import Profile
from dashboard.forms import UserUpdateForm, ProfileUpdateForm
from payment.models import Order, Transaction


def is_admin_user(user):
    return user.is_active and (user.is_staff or user.is_superuser)


@login_required
def index(request):
    if request.user.user_type == 'Buyer':
        return redirect('dashboard:buyer')
    if request.user.is_superuser or request.user.is_staff:
        return redirect('dashboard:admin')
    return seller_dashboard(request)


@login_required
def seller_dashboard(request):
    from cart.models import Sale
    from item.models import Review
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
    inventory_value = active_items.aggregate(total=Sum('original_price'))['total'] or 0

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

    # Orders — seller এর items এর orders
    seller_orders = Order.objects.filter(
        item__user=request.user
    ).select_related('item', 'buyer', 'transaction').order_by('-created_at')[:10]

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
        'orders': seller_orders,
    })


@login_required
def buyer_dashboard(request):
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

    buyer_orders = Order.objects.filter(
        buyer=request.user
    ).select_related('item', 'transaction').order_by('-created_at')[:10]

    from core.models import Wishlist
    wishlist = Wishlist.objects.filter(
        user=request.user
    ).select_related('item', 'item__category')[:10]

    return render(request, 'dashboard/buyer.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'orders': buyer_orders,
        'wishlist': wishlist,
    })


@login_required
@user_passes_test(is_admin_user, login_url='core:index')
def admin_dashboard(request):
    from dashboard.admin_stats import build_admin_dashboard_data
    data = build_admin_dashboard_data()
    return render(request, 'dashboard/admin.html', data)


# ── ✅ User Management Actions ──

@login_required
@user_passes_test(is_admin_user, login_url='core:index')
@require_POST
def freeze_user(request, user_id):
    """User freeze করো — login করতে পারবে না"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    target = get_object_or_404(User, pk=user_id)

    # নিজেকে বা অন্য superuser-কে freeze করা যাবে না
    if target == request.user:
        messages.error(request, "আপনি নিজেকে freeze করতে পারবেন না।")
        return redirect('dashboard:admin')
    if target.is_superuser:
        messages.error(request, "Superuser-কে freeze করা যাবে না।")
        return redirect('dashboard:admin')

    target.is_frozen = True
    target.save(update_fields=['is_frozen'])
    messages.success(request, f"✅ '{target.username}' freeze করা হয়েছে।")
    return redirect('dashboard:admin')


@login_required
@user_passes_test(is_admin_user, login_url='core:index')
@require_POST
def unfreeze_user(request, user_id):
    """User unfreeze করো — আবার login করতে পারবে"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    target = get_object_or_404(User, pk=user_id)
    target.is_frozen = False
    target.is_spam = False  # ✅ unfreeze করলে spam-ও clear হবে
    target.save(update_fields=['is_frozen', 'is_spam'])
    messages.success(request, f"✅ '{target.username}' unfreeze ও normal করা হয়েছে।")
    return redirect('dashboard:admin')


@login_required
@user_passes_test(is_admin_user, login_url='core:index')
@require_POST
def mark_spam_user(request, user_id):
    """User-কে spam mark করো"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    target = get_object_or_404(User, pk=user_id)

    if target == request.user or target.is_superuser:
        messages.error(request, "এই user-কে spam mark করা যাবে না।")
        return redirect('dashboard:admin')

    target.is_spam = True
    target.is_frozen = True  # spam হলে automatically freeze
    target.save(update_fields=['is_spam', 'is_frozen'])
    messages.success(request, f"⚠️ '{target.username}' spam mark ও freeze করা হয়েছে।")
    return redirect('dashboard:admin')


@login_required
@user_passes_test(is_admin_user, login_url='core:index')
@require_POST
def delete_user(request, user_id):
    """User delete করো — confirm required"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    target = get_object_or_404(User, pk=user_id)
    confirm = request.POST.get('confirm_delete')

    if target == request.user:
        messages.error(request, "আপনি নিজেকে delete করতে পারবেন না।")
        return redirect('dashboard:admin')
    if target.is_superuser:
        messages.error(request, "Superuser-কে delete করা যাবে না।")
        return redirect('dashboard:admin')
    if confirm != 'DELETE':
        messages.error(request, "Delete confirm করা হয়নি। 'DELETE' টাইপ করুন।")
        return redirect('dashboard:admin')

    username = target.username
    target.delete()
    messages.success(request, f"🗑️ '{username}' সম্পূর্ণ delete করা হয়েছে।")
    return redirect('dashboard:admin')


@login_required
def orders(request):
    if request.user.user_type == 'Buyer':
        all_orders = Order.objects.filter(
            buyer=request.user
        ).select_related('item', 'transaction').order_by('-created_at')
    else:
        all_orders = Order.objects.filter(
            item__user=request.user
        ).select_related('item', 'buyer', 'transaction').order_by('-created_at')

    return render(request, 'dashboard/orders.html', {
        'orders': all_orders,
    })


@login_required
def update_order_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if not (request.user == order.item.user or request.user.is_staff):
        messages.error(request, "You don't have permission.")
        return redirect('dashboard:orders')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]

        if new_status in valid_statuses:
            order.status = new_status
            order.add_tracking_event(
                new_status,
                f'Status updated to {order.get_status_display()}',
            )

            if new_status == 'delivered':
                from django.utils import timezone
                order.delivered_at = timezone.now()

            order.save()

            from core.email_utils import send_order_status_update
            send_order_status_update(order)

            from core.models import Notification
            Notification.objects.create(
                user=order.buyer,
                title="Order Update 📦",
                message=f"Your order for '{order.item.name}' is now: {order.get_status_display()}",
                notification_type='general',
                link=f"/payment/track/{order.order_number}/",
            )
            messages.success(request, f"Order updated: {order.get_status_display()}")
        else:
            messages.error(request, "Invalid status.")

    return redirect('dashboard:orders')