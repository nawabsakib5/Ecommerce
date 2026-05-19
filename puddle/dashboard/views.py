from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from item.models import Item
from .models import Profile 
from .forms import UserUpdateForm, ProfileUpdateForm


@login_required
def index(request):
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    items = Item.objects.filter(user=request.user).select_related('category')

    

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
        'u_form': u_form,
        'p_form': p_form,
        
    }
    return render(request, 'dashboard/index.html', context)