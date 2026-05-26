import random
from faker import Faker
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Item, Category
from .seed_helpers import seed_admin_catalog

fake = Faker()
User = get_user_model()

CATEGORY_NAMES = [
    'Electronics', 'Clothing', 'Books', 'Furniture', 'Sports',
    'Toys', 'Vehicles', 'Food', 'Beauty', 'Music',
    'Gaming', 'Jewelry', 'Tools', 'Garden', 'Pets',
    'Baby', 'Office', 'Art', 'Travel', 'Fitness',
    'Kitchen', 'Shoes', 'Bags', 'Watches', 'Cameras',
    'Phones', 'Laptops', 'Tablets', 'TVs', 'Audio',
    'Lighting', 'Bedding', 'Cleaning', 'Stationery', 'Crafts',
    'Outdoors', 'Fishing', 'Cycling', 'Swimming', 'Yoga',
    'Cooking', 'Baking', 'Coffee', 'Tea', 'Wine',
    'Comics', 'Movies', 'Anime', 'Collectibles', 'Vintage',
]


def get_or_create_categories():
    categories = []
    for name in CATEGORY_NAMES:
        cat, _ = Category.objects.get_or_create(name=name)
        categories.append(cat)
    return categories


def create_items_per_category(user):
    categories = Category.objects.all()
    if not categories.exists():
        return

    items_to_create = []
    for category in categories:
        existing = Item.objects.filter(
            user=user, category=category
        ).count()
        needed = max(0, 2 - existing)
        for _ in range(needed):
            items_to_create.append(Item(
                category=category,
                user=user,
                name=fake.word().capitalize() + " " + fake.word().capitalize(),
                description=fake.paragraph(nb_sentences=3),
                price=round(random.uniform(10, 1000), 2),
                is_sold=False,
            ))

    if items_to_create:
        Item.objects.bulk_create(items_to_create)
        print(f"[SEED] {user.username} — {len(items_to_create)} items created!")


# ✅ Migration এর পরে admin catalog seed
@receiver(post_migrate)
def seed_after_migrate(sender, **kwargs):
    if sender.name != 'item':
        return
    seed_admin_catalog()


# ✅ Item save হলে category cache clear
@receiver(post_save, sender=Item)
def clear_category_cache(sender, **kwargs):
    cache.delete('all_categories')


# ✅ User login করলে auto seed
@receiver(user_logged_in)
def seed_on_login(sender, request, user, **kwargs):
    create_items_per_category(user)


# ✅ নতুন user signup করলে auto seed
@receiver(post_save, sender=User)
def seed_on_signup(sender, instance, created, **kwargs):
    if not created:
        return
    create_items_per_category(instance)


# ✅ Item sell হলে seller কে notification পাঠাবে
@receiver(post_save, sender=Item)
def notify_on_sale(sender, instance, created, **kwargs):
    if created:
        return

    if instance.is_sold:
        from core.models import Notification

        already = Notification.objects.filter(
            user=instance.user,
            title="Item Sold! 🎉",
            message__contains=instance.name
        ).exists()

        if not already:
            Notification.objects.create(
                user=instance.user,
                title="Item Sold! 🎉",
                message=f"Your item '{instance.name}' has been sold for ${instance.price}",
                notification_type='sale',
                link=f"/items/{instance.id}/",
            )