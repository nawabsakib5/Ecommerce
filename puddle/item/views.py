from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.db.models import Q
from django.core.paginator import Paginator


def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    items_list = Item.objects.filter(is_sold=False)

    if category_id:
        items_list = items.filter(category_id= category_id)


    if query:
        items_list = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(items_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'item/items.html', {
        'items':page_obj,
        'query':query,
        'categories' : categories,
        'category_id' : int(category_id),
    })



def detail(request, pk):

    item = get_object_or_404(Item , pk=pk)
    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk)[0:3]

    return render(request , 'item/detail.html', {
        'item':item,
        'related_items':related_items,
    })


@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit= False)
            item.user = request.user
            item.save()

            return redirect ('item:detail', pk=item.id )
        
    else:
        form = NewItemForm()


    return render(request, 'item/form.html', {
        'form' : form,
        'title' : 'New item',
    })


@login_required
def edit(request , pk):
    item = get_object_or_404(Item ,pk =pk, user= request.user)
    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()

            return redirect ('item:detail', pk=item.id )
        
    else:
        form = EditItemForm(instance=item)


    return render(request, 'item/form.html', {
        'form' : form,
        'title' : 'Edit item',
    })


@login_required
def delete(request, pk):
    item = get_object_or_404(Item ,pk =pk, user= request.user)
    item.delete()

    return redirect('dashboard:index')