from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from item.models import Item
from .models import Cart, CartItem, Sale, Order, OrderItem



def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart



@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__category').all()
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })



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
    if request.user.user_type != 'Buyer':
        messages.error(request, "Only buyers can checkout!")
        return redirect('dashboard:index')

    cart = get_or_create_cart(request.user)
    cart_items = cart.cart_items.select_related('item', 'item__user').all()

    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:detail')

    
    sold_items = [ci for ci in cart_items if ci.item.is_sold]
    if sold_items:
        for ci in sold_items:
            messages.error(request, f"'{ci.item.name}' is already sold! Removed from cart.")
            ci.delete()
        return redirect('cart:detail')

    if request.method == 'POST':
        
        shipping_address = request.POST.get('shipping_address', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not shipping_address:
            messages.error(request, "Shipping address is required!")
            return render(request, 'cart/checkout.html', {
                'cart': cart,
                'cart_items': cart_items,
            })

        if not phone:
            messages.error(request, "Phone number is required!")
            return render(request, 'cart/checkout.html', {
                'cart': cart,
                'cart_items': cart_items,
            })

        total = cart.get_total()

        order = Order.objects.create(
            buyer=request.user,
            total_amount=total,
            status='pending',
            shipping_address=shipping_address,
            phone=phone,
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

            
            try:
                from core.models import Notification
                Notification.objects.create(
                    user=item.user,
                    message=f"🎉 '{item.name}' has been sold to {request.user.username}!",
                )
            except Exception:
                pass

        
        cart.cart_items.all().delete()

        messages.success(request, f"Order #{order.id} placed successfully! 🎉")
        return redirect('cart:order_detail', pk=order.id)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total(),
    })



@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'order_items__item',
            'order_items__seller',
        ),
        pk=pk,
        buyer=request.user,
    )
    return render(request, 'cart/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(
        buyer=request.user
    ).prefetch_related(
        'order_items__item'
    ).order_by('-created_at')

    return render(request, 'cart/order_history.html', {'orders': orders})