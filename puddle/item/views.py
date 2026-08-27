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
    from .models import Review
    from django.db.models import Avg

    item = get_object_or_404(
        Item.objects.select_related('category', 'user', 'shop'),
        pk=pk,
    )

    extra_images = item.images.all()

    related_items = Item.objects.filter(
        category=item.category,
        is_sold=False,
        status='active',
    ).exclude(pk=pk).select_related('category', 'user')[:4]

    reviews = Review.objects.filter(item=item).select_related('user')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items,
        'extra_images': extra_images,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
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

            # Extra images save — max 5MB each
            from .models import ItemImage
            extra_images = request.FILES.getlist('extra_images')
            for i, img in enumerate(extra_images[:5]):
                if img.size > 5 * 1024 * 1024:
                    messages.warning(request, f"'{img.name}' is too large. Max 5MB per image.")
                    continue
                ItemImage.objects.create(item=item, image=img, order=i)

            # Video save — max 50MB
            product_video = request.FILES.get('product_video')
            if product_video:
                if product_video.size > 50 * 1024 * 1024:
                    messages.warning(request, "Video too large. Max 50MB allowed.")
                else:
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

            # নতুন extra images যোগ করা — max 5MB each
            from .models import ItemImage
            extra_images = request.FILES.getlist('extra_images')
            for i, img in enumerate(extra_images[:5]):
                if img.size > 5 * 1024 * 1024:
                    messages.warning(request, f"'{img.name}' is too large. Max 5MB per image.")
                    continue
                existing_count = item.images.filter(media_type='image').count()
                ItemImage.objects.create(item=item, image=img, order=existing_count + i)

            # নতুন video যোগ করা — max 50MB
            product_video = request.FILES.get('product_video')
            if product_video:
                if product_video.size > 50 * 1024 * 1024:
                    messages.warning(request, "Video too large. Max 50MB allowed.")
                else:
                    item.images.filter(media_type='video').delete()
                    ItemImage.objects.create(
                        item=item,
                        video=product_video,
                        media_type='video',
                        order=99
                    )

            # পুরানো images delete request
            delete_ids = request.POST.getlist('delete_image')
            if delete_ids:
                item.images.filter(id__in=delete_ids).delete()

            messages.success(request, "Item updated successfully!")
            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    # Existing media pass করো template এ
    existing_images = item.images.filter(media_type='image')
    existing_video = item.images.filter(media_type='video').first()

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit Item',
        'item': item,
        'existing_images': existing_images,
        'existing_video': existing_video,
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



@login_required
def add_review(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    # নিজের item-এ review দেওয়া যাবে না
    if request.user == item.user:
        messages.error(request, "You cannot review your own item.")
        return redirect('item:detail', pk=item_id)

    # Verified purchase check
    from payment.models import Order
    from .models import Review
    verified = Order.objects.filter(
        buyer=request.user,
        item=item,
        status__in=['delivered', 'confirmed']
    ).exists()

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        image = request.FILES.get('review_image')

        if not body:
            messages.error(request, "Review body cannot be empty.")
            return redirect('item:detail', pk=item_id)

        review, created = Review.objects.update_or_create(
            user=request.user,
            item=item,
            defaults={
                'rating': rating,
                'title': title,
                'body': body,
                'is_verified_purchase': verified,
                'image': image if image else None,
            }
        )

        if created:
            messages.success(request, "Review submitted! ⭐")
        else:
            messages.success(request, "Review updated! ⭐")

    return redirect('item:detail', pk=item_id)