import random

from django.contrib.auth import get_user_model

from item.models import Category, Item

User = get_user_model()

DEFAULT_CATEGORIES = ('Electronics', 'Furniture', 'Clothing')
ADMIN_ITEM_TARGET = 1000
USER_ITEMS_PER_CATEGORY = 2

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

def create_items_per_category(user, per_category=USER_ITEMS_PER_CATEGORY):
    ensure_categories()
    categories = Category.objects.all()
    if not categories.exists():
        return 0

    items_to_create = []
    for category in categories:
        for i in range(per_category):
            items_to_create.append(
                Item(
                    category=category,
                    user=user,
                    name=f'{category.name} — {user.username} #{i + 1}',
                    description='Auto-generated item for this user.',
                    price=round(random.uniform(10, 1000), 2),
                    is_sold=False,
                )
            )

    if items_to_create:
        Item.objects.bulk_create(items_to_create)
    return len(items_to_create)

def seed_admin_items(admin_user=None, target_count=ADMIN_ITEM_TARGET):
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

    items_to_create = []
    for index, category in enumerate(categories):
        count = per_category + (1 if index < extra else 0)
        for _ in range(count):
            items_to_create.append(
                Item(
                    category=category,
                    user=admin_user,
                    name=f'{category.name} Bulk #{existing + len(items_to_create) + 1}',
                    description='Admin catalog item (category-wise seed).',
                    price=round(random.uniform(10, 500), 2),
                    is_sold=False,
                )
            )

    if items_to_create:
        Item.objects.bulk_create(items_to_create, batch_size=500)
    return len(items_to_create)