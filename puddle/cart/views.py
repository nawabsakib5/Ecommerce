from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from item.models import Item
from .models import Cart, CartItem, Sale


# ── Helper ──
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# ── Cart Detail ──
@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__category').all()
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


# ── Add to Cart ──
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if item.user == request.user:
        messages.error(request, "You cannot buy your own item!")
        return redirect('item:detail', pk=item_id)

    if item.is_sold:
        messages.error(request, "Sorry, this item is already sold!")
        return redirect('item:detail', pk=item_id)

    if request.user.user_type != 'Buyer':
        messages.error(request, "Only buyers can add items to cart!")
        return redirect('item:detail', pk=item_id)

    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, item=item, defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"'{item.name}' quantity updated!")
    else:
        messages.success(request, f"'{item.name}' added to cart! 🛒")

    return redirect('cart:detail')


# ── Remove from Cart ──
@login_required
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:detail')


# ── Update Quantity ──
@login_required
def update_quantity(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Quantity updated!")

    return redirect('cart:detail')


# ── ✅ Checkout — payment app-এ redirect করো ──
# আগে এখানে directly item sold করা হতো — payment ছাড়াই
# এখন শুধু cart-এ একটা item থাকলে payment checkout-এ পাঠাও
# একাধিক item থাকলে user-কে জানাও একটা একটা করে checkout করতে
@login_required
def checkout(request):
    if request.user.user_type != 'Buyer':
        messages.error(request, "Only buyers can checkout!")
        return redirect('dashboard:index')

    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__user').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:detail')

    # Sold হয়ে গেছে এমন item সরাও
    sold_items = [ci for ci in cart_items if ci.item.is_sold]
    if sold_items:
        for ci in sold_items:
            messages.error(request, f"'{ci.item.name}' is already sold! Removed from cart.")
            ci.delete()
        return redirect('cart:detail')

    # ✅ Cart-এ একটাই item — সরাসরি payment checkout-এ পাঠাও
    cart_items = cart.cart_items.select_related('item').all()
    if cart_items.count() == 1:
        item = cart_items.first().item
        return redirect('payment:checkout', item_pk=item.pk)

    # ✅ একাধিক item — user-কে বলো একটা একটা করে checkout করতে
    # (payment app single-item checkout করে, multi-item future feature)
    messages.info(
        request,
        "Please checkout items one at a time — click 'Buy Now' on each item."
    )
    return redirect('cart:detail')


# ── Order Detail — payment app-এর tracking-এ redirect ──
@login_required
def order_detail(request, pk):
    # পুরনো cart.Order ছিল — এখন payment.Order ব্যবহার হয়
    # পুরনো link কাজ করার জন্য dashboard orders-এ পাঠাও
    messages.info(request, "View your orders here.")
    return redirect('dashboard:orders')


# ── Order History — dashboard orders-এ redirect ──
@login_required
def order_history(request):
    return redirect('dashboard:orders')