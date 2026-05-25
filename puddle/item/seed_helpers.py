import random

import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from item.models import Category, Item

User = get_user_model()

DEFAULT_CATEGORIES = ('Electronics', 'Furniture', 'Clothing')
ADMIN_CATALOG_TARGET = 50
PICSUM_SIZE = '400/400'

def is_admin_user(user):
    if not user:
        return False
    return (
        user.is_superuser
        or user.is_staff
        or getattr(user, 'user_type', None) == 'Admin'
    )

def get_admin_user():
    return (
        User.objects.filter(is_superuser=True).order_by('pk').first()
        or User.objects.filter(user_type='Admin').order_by('pk').first()
        or User.objects.filter(is_staff=True).order_by('pk').first()
    )

def ensure_categories():
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name)

def attach_image_from_picsum(item, seed):
    url = f'https://picsum.photos/seed/{seed}/{PICSUM_SIZE}'
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    filename = f'{seed}.jpg'
    item.image.save(filename, ContentFile(response.content), save=True)

def seed_admin_catalog(admin_user=None, target_count=ADMIN_CATALOG_TARGET):
    ensure_categories()
    admin_user = admin_user or get_admin_user()
    if not admin_user:
        return 0

    categories = list(Category.objects.all())
    if not categories:
        return 0

    existing = Item.objects.filter(user=admin_user).count()
    if existing >= target_count:
        return 0

    remaining = target_count - existing
    per_category = remaining // len(categories)
    extra = remaining % len(categories)

    created = 0
    for index, category in enumerate(categories):
        count = per_category + (1 if index < extra else 0)
        for i in range(count):
            seed = f'admin-{admin_user.pk}-{category.pk}-{existing + created}'
            item = Item(
                category=category,
                user=admin_user,
                name=f'{category.name} Store #{existing + created + 1}',
                description='Marketplace catalog item from admin.',
                price=round(random.uniform(10, 500), 2),
                is_sold=False,
            )
            item.save()
            try:
                attach_image_from_picsum(item, seed)
            except requests.RequestException:
                pass
            created += 1

    return created

def seed_admin_items(admin_user=None, target_count=ADMIN_CATALOG_TARGET):
    return seed_admin_catalog(admin_user, target_count)