from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import render, redirect

from item.models import Item
from item.seed_helpers import is_admin_user

from .admin_stats import build_admin_dashboard_data
from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile


@login_required
def index(request):
    # ✅ Seller আর Buyer আলাদা dashboard এ যাবে
    if request.user.user_type == 'Buyer':
        return redirect('dashboard:buyer')
    return seller_dashboard(request)


@login_required
def seller_dashboard(request):
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

    return render(request, 'dashboard/index.html', {
        'items': items,
        'active_count': active_items.count(),
        'sold_count': sold_items.count(),
        'inventory_value': round(inventory_value, 2),
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
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

    # Buyer এর cart items
    from cart.models import Cart
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.select_related('item', 'item__category').all()

    return render(request, 'dashboard/buyer.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'cart': cart,
        'cart_items': cart_items,
    })


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    context = build_admin_dashboard_data()
    return render(request, 'dashboard/admin.html', context)