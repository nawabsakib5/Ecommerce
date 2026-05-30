from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Wishlist, WishlistItem
from item.models import Item

@login_required
def wishlist_detail(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('item').all()
    return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist, 'items': items})


@login_required
def add_to_wishlist(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, item=item)
    if created:
        messages.success(request, f"'{item.name}' added to wishlist!")
    else:
        messages.info(request, f"'{item.name}' is already in your wishlist.")
    return redirect('wishlist:detail')


@login_required
def remove_from_wishlist(request, item_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist_item = get_object_or_404(WishlistItem, wishlist=wishlist, item_id=item_id)
    wishlist_item.delete()
    messages.success(request, "Item removed from wishlist.")
    return redirect('wishlist:detail')
