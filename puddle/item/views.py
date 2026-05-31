from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache

from .models import Item, Category
from .forms import NewItemForm, EditItemForm


def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)

    categories = cache.get_or_set('all_categories', Category.objects.all(), 3600)

    items_list = (
        Item.objects.filter(is_sold=False)
        .select_related('category', 'user')
        .order_by('-created_at')
    )

    if category_id and int(category_id) != 0:
        items_list = items_list.filter(category_id=category_id)

    if query:
        items_list = items_list.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

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
    item = get_object_or_404(
        Item.objects.select_related('category', 'user'),
        pk=pk,
    )

    related_items = Item.objects.filter(
        category=item.category,
        is_sold=False
    ).exclude(pk=pk).select_related('category', 'user')[:3]

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
    })


@login_required
def new(request):
    if request.user.user_type == 'Buyer':
        messages.error(request, "Buyers cannot add items. Please create a Seller account.")
        return redirect('item:items')

    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            cache.delete('all_categories')
            messages.success(
                request,
                'Your item is live — everyone can browse and add it to cart.',
            )
            return redirect('item:detail', pk=item.id)
    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'New Item',
    })


@login_required
def edit(request, pk):
    if request.user.user_type == 'Buyer':
        messages.error(request, "Buyers cannot edit items.")
        return redirect('item:items')

    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit Item',
    })


@login_required
def delete(request, pk):
    if request.user.user_type == 'Buyer':
        messages.error(request, "Buyers cannot delete items.")
        return redirect('item:items')

    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully!")
        return redirect('dashboard:index')

    return render(request, 'item/delete_confirm.html', {
        'item': item,
    })