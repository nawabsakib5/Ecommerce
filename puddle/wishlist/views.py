from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from item.models import Item
from core.models import Wishlist  # ✅ core.Wishlist ব্যবহার করো — duplicate model না


# ── Wishlist Detail ──
@login_required
def wishlist_detail(request):
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related('item', 'item__category').order_by('-added_at')
    return render(request, 'wishlist/wishlist.html', {'wishlist': items})


# ── Add to Wishlist ──
@login_required
def add_to_wishlist(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        item=item
    )
    if created:
        messages.success(request, f"'{item.name}' added to wishlist! ❤️")
    else:
        messages.info(request, f"'{item.name}' is already in your wishlist.")
    return redirect('wishlist:detail')


# ── Remove from Wishlist ──
@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        item_id=item_id
    )
    wishlist_item.delete()
    messages.success(request, "Item removed from wishlist.")
    return redirect('wishlist:detail')