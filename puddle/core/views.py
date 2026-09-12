from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, update_session_auth_hash, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse

from item.models import Item, Category
from .forms import SignupForm
from .models import Notification, Wishlist
from item.models import Review


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

        # reCAPTCHA verify
        recaptcha_response = request.POST.get('g-recaptcha-response')
        import requests as req
        from django.conf import settings
        r = req.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        })
        result = r.json()
        score = result.get('score', 0)

        if not result.get('success') or score < 0.5:
            messages.error(request, "Security check failed. Please try again.")
            return render(request, 'core/signup.html', {'form': form})

        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # ✅ Welcome email পাঠাও
            from core.email_utils import send_welcome_email
            send_welcome_email(user)

            return redirect('core:index')
    else:
        form = SignupForm()

    from django.conf import settings
    return render(request, 'core/signup.html', {
        'form': form,
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
    })


@login_required
def changePass(request):
    if request.method == "POST":
        old_pass = request.POST.get('old_pass')
        new_pass = request.POST.get('new_pass')
        con_pass = request.POST.get('con_pass')

        # ── পুরনো password চেক ──
        if not request.user.check_password(old_pass):
            messages.error(request, "Old password is incorrect.")
            return render(request, 'core/changePass.html')

        # ── নতুন password match চেক ──
        if new_pass != con_pass:
            messages.error(request, "New passwords do not match.")
            return render(request, 'core/changePass.html')

        # ── ✅ Django password validator দিয়ে strength চেক ──
        # এটা settings.py-এর AUTH_PASSWORD_VALIDATORS ব্যবহার করে
        # (min 8 chars, not common, not numeric only, not similar to username)
        try:
            validate_password(new_pass, user=request.user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'core/changePass.html')

        # ── সব ঠিক আছে — password change করো ──
        request.user.set_password(new_pass)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully! 🔒")
        return redirect('core:index')

    return render(request, 'core/changePass.html')


@login_required
def generate_password_suggestion(request):
    """
    ✅ Strong password suggestion generate করো — AJAX call
    Password pattern: 2 uppercase + 4 lowercase + 2 digits + 2 special chars
    মোট ১২ characters — সহজে মনে রাখা যায় এমন format
    """
    import random
    import string

    uppercase = random.choices(string.ascii_uppercase, k=2)
    lowercase = random.choices(string.ascii_lowercase, k=6)
    digits = random.choices(string.digits, k=2)
    special = random.choices('@#$!%*?&', k=2)

    # সব মিলিয়ে shuffle করো
    all_chars = uppercase + lowercase + digits + special
    random.shuffle(all_chars)
    password = ''.join(all_chars)

    return JsonResponse({'password': password})


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
        action = 'removed'
        msg = f"'{item.name}' removed from wishlist."
    else:
        action = 'added'
        msg = f"'{item.name}' added to wishlist! ❤️"

    # AJAX request হলে JSON response দাও
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'action': action, 'message': msg})

    # Normal request হলে redirect
    messages.success(request, msg)
    return redirect('item:detail', pk=item_id)


def help_center(request):
    return render(request, 'core/help_center.html')


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related('item', 'item__category').order_by('-added_at')
    return render(request, 'core/wishlist.html', {'wishlist': items})