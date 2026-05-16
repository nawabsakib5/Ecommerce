from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from item.models import Item
from .models import Profile 
from .forms import UserUpdateForm, ProfileUpdateForm
from payment.models import Order, BillingAddress

@login_required
def index(request):
    # প্রোফাইল না থাকলে তৈরি করবে
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # অপ্টিমাইজড কুয়েরি (রেলওয়েতে ফাস্ট চলার জন্য)
    items = Item.objects.filter(user=request.user).select_related('category')
    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')

    # বিলিং অ্যাড্রেস চেক
    billing_info = BillingAddress.objects.filter(user=request.user).first()
    address_complete = billing_info.is_fully_filled() if billing_info else False

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('dashboard:index')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'items': items,
        'orders': orders,
        'u_form': u_form,
        'p_form': p_form,
        'address_complete': address_complete,
    }
    return render(request, 'dashboard/index.html', context)