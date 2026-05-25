from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from item.models import Item

from .models import Cart, CartItem, Sale


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related(
        'item', 'item__category'
    ).all()
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart = get_or_create_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        item=item,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"'{item.name}' quantity updated!")
    else:
        messages.success(request, f"'{item.name}' added to cart!")

    return redirect('cart:detail')


@login_required
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:detail')


@login_required
def update_quantity(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)

    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Quantity updated!")

    return redirect('cart:detail')


@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:detail')

    if request.method == 'POST':
        for cart_item in cart_items:
            item = cart_item.item
            total = cart_item.get_subtotal()
            commission = Sale.calc_commission(total)
            Sale.objects.create(
                item=item,
                seller=item.user,
                buyer=request.user,
                quantity=cart_item.quantity,
                unit_price=item.price,
                total_amount=total,
                commission_amount=commission,
            )
            item.is_sold = True
            item.save()
        cart.cart_items.all().delete()
        messages.success(request, "Order placed successfully!")
        return redirect('item:items')

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
    })