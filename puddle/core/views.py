from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from item.models import Item, Category
from .forms import SignupForm
from .models import Notification, Wishlist, Review


def index(request):
    now = timezone.now()

    # Flash sale items
    flash_items = (
        Item.objects.filter(
            is_sold=False,
            status='active',
            sale_price__isnull=False,
            sale_start__lte=now,
            sale_end__gte=now,
        )
        .select_related('category', 'user', 'shop')
        .order_by('-created_at')[:8]
    )

    # Latest items
    items = (
        Item.objects.filter(is_sold=False, status='active')
        .select_related('category', 'user', 'shop')
        .order_by('-created_at')[:12]
    )

    categories = Category.objects.all().order_by('name')

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
        'flash_items': flash_items,
        'now': now,
    })


def contact(request):
    return render(request, 'core/contact.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('core:index')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


@login_required
def changePass(request):
    if request.method == "POST":
        old_pass = request.POST.get('old_pass')
        new_pass = request.POST.get('new_pass')
        con_pass = request.POST.get('con_pass')

        if request.user.check_password(old_pass):
            if new_pass == con_pass:
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password changed successfully!")
                return redirect('core:index')
            else:
                messages.error(request, "New passwords do not match.")
        else:
            messages.error(request, "Old password is incorrect.")

    return render(request, 'core/changePass.html')


def logoutpage(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('core:login')


@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {
        'notifications': notifs,
    })


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('core:notifications')


@login_required
def toggle_wishlist(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, item=item
    )
    if not created:
        wishlist_item.delete()
        messages.success(request, f"'{item.name}' removed from wishlist.")
    else:
        messages.success(request, f"'{item.name}' added to wishlist! ❤️")
    return redirect('item:detail', pk=item_id)


@login_required
def add_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.update_or_create(
            user=request.user,
            item=item,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Review submitted! ⭐")
    return redirect('item:detail', pk=item_id)


def help_center(request):
    return render(request, 'core/help_center.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')
