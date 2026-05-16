from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Category
from django.contrib.auth.decorators import login_required
from .forms import NewItemForm, EditItemForm
from django.db.models import Q
from django.core.paginator import Paginator

def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    
    # মডেলে 'user' ফিল্ড আছে তাই 'user' ইমপোর্ট করা হলো
    items_list = Item.objects.filter(is_sold=False).select_related('category', 'user')

    if category_id and int(category_id) != 0:
        items_list = items_list.filter(category_id=category_id)

    if query:
        items_list = items_list.filter(Q(name__icontains=query) | Q(description__icontains=query))

    paginator = Paginator(items_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'item/items.html', {
        'items': page_obj,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })

def detail(request, pk):
    # এখানে 'created_by' এর বদলে 'user' ব্যবহার করুন
    item = get_object_or_404(Item.objects.select_related('category', 'user'), pk=pk)
    
    related_items = Item.objects.filter(category=item.category, is_sold=False).exclude(pk=pk).select_related('category', 'user')[:3]

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
            item.user = request.user # সঠিক ফিল্ড নেম 'user'
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
    # এখানেও 'user' ব্যবহার করুন
    item = get_object_or_404(Item, pk=pk, user=request.user)
    
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