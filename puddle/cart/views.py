from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from item.models import Item
from .models import Cart, CartItem, Sale, Order, OrderItem


# 🟢 Order History
@login_required
def order_history(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related('order_items__item').order_by('-created_at')
    return render(request, 'cart/order_history.html', {'orders': orders})


# 🟢 Cart Utility
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# 🟢 Cart Detail
@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__category').all()
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


# 🟢 Add to Cart
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart = get_or_create_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, item=item, defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"'{item.name}' quantity updated!")
    else:
        messages.success(request, f"'{item.name}' added to cart!")

    return redirect('cart:detail')


# 🟢 Remove from Cart
@login_required
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:detail')


# 🟢 Update Quantity
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


# 🟢 Checkout
@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__user').all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:detail')

    if request.method == 'POST':
        total = cart.get_total()

        # ✅ Create Order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total,
            status='pending',
        )

        for cart_item in cart_items:
            item = cart_item.item
            subtotal = cart_item.get_subtotal()
            commission = Sale.calc_commission(subtotal)

            # ✅ Create OrderItem
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=cart_item.quantity,
                price=item.price,
                seller=item.user,
            )

            # ✅ Create Sale record
            Sale.objects.create(
                item=item,
                seller=item.user,
                buyer=request.user,
                quantity=cart_item.quantity,
                unit_price=item.price,
                total_amount=subtotal,
                commission_amount=commission,
            )

            # ✅ Mark item as sold
            item.is_sold = True
            item.save()

        cart.cart_items.all().delete()
        messages.success(request, f"Order #{order.id} placed successfully! 🎉")
        return redirect('cart:order_detail', pk=order.id)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


# 🟢 Order Detail
@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'order_items__item',
            'order_items__seller'
        ),
        pk=pk,
        buyer=request.user
    )
    return render(request, 'cart/order_detail.html', {'order': order})
