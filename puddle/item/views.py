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
    
    # এখানে select_related যোগ করা হয়েছে যা category এবং user এর তথ্য একবারে নিয়ে আসবে
    items_list = Item.objects.filter(is_sold=False).select_related('category', 'created_by')

    if category_id:
        items_list = items_list.filter(category_id=category_id)

    if query:
        items_list = items_list.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # প্যাগিনেশন (প্রতি পেজে ২৫টি আইটেম)
    paginator = Paginator(items_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'item/items.html', {
        'items': page_obj,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })

def detail(request, pk):
    # ডিটেইল পেজেও select_related ব্যবহার করা ভালো
    item = get_object_or_404(Item.objects.select_related('category', 'created_by'), pk=pk)
    
    # রিলেটেড আইটেম দেখানোর সময়ও অপ্টিমাইজেশন করা হয়েছে
    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk).select_related('category', 'created_by')[0:3]

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
    })

@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user # আপনার মডেলে ফিল্ডের নাম অনুযায়ী এটি চেক করে নিন
            item.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'New item',
    })

@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()

            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit item',
    })

@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()

    return redirect('dashboard:index')