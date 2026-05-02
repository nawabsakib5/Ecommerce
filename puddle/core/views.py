from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib import messages
from item.models import *
from .forms import*
from django.contrib.auth import update_session_auth_hash


def index(request):
    items = Item.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()

    return render(request , 'core/index.html',{
        'categories': categories,
        'items' : items,
    })


def contact(request):
    return render(request, 'core/contact.html')


def signup(request):
    if request.method == 'POST':
        form = SignupFrom(request.POST)

        if form.is_valid():
            form.save()
            return redirect('core:login')
    else:
        form = SignupFrom()

    return render(request, 'core/signup.html', {
    'form': form
})

def changePass(request):
    user=request.user
    if request.method == "POST":
      old_pass=request.POST.get('old_pass')
      new_pass = request.POST.get('new_pass')
      con_pass = request.POST.get('con_pass')
      if user.check_password(old_pass):
        if con_pass==new_pass:
            user.set_password(new_pass)
            user.save()
            update_session_auth_hash(request,user)
            return redirect('core:index')
        
    return render(request,'core/changePass.html')

def logoutpage(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect ('core:login')