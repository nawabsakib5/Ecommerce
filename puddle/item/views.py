from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils import timezone

from .models import Item, Category
from .forms import NewItemForm, EditItemForm


def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)

    categories = cache.get_or_set('all_categories', Category.objects.all(), 3600)

    items_list = (
        Item.objects.filter(is_sold=False, status='active')
        .select_related('category', 'user', 'shop')
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

    # Flash sale items
    now = timezone.now()
    flash_items = (
        Item.objects.filter(
            is_sold=False,
            status='active',
            sale_price__isnull=False,
            sale_start__lte=now,
            sale_end__gte=now,
        )
        .select_related('category', 'user', 'shop')
        .order_by('-created_at')[:8]
    )

    return render(request, 'item/items.html', {
        'items': page_obj,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
        'flash_items': flash_items,
    })


def detail(request, pk):
    item = get_object_or_404(
        Item.objects.select_related('category', 'user', 'shop'),
        pk=pk,
    )

    # Multiple images — main image + extra images
    extra_images = item.images.all()

    related_items = Item.objects.filter(
        category=item.category,
        is_sold=False,
        status='active',
    ).exclude(pk=pk).select_related('category', 'user')[:4]

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
        'extra_images': extra_images,
    })


@login_required
def new(request):
    if request.user.user_type == 'Buyer':
        messages.error(request, "Buyers cannot add items.")
        return redirect('item:items')

    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            if hasattr(request.user, 'shop'):
                item.shop = request.user.shop
            item.save()

            # Extra images save
            from .models import ItemImage
            extra_images = request.FILES.getlist('extra_images')
            for i, img in enumerate(extra_images[:5]):
                ItemImage.objects.create(item=item, image=img, order=i)

            # Video save
            product_video = request.FILES.get('product_video')
            if product_video:
                ItemImage.objects.create(
                    item=item,
                    video=product_video,
                    media_type='video',
                    order=99
                )

            cache.delete('all_categories')
            messages.success(request, 'Your item is live!')
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