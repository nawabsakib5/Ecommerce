import random
from faker import Faker
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from .models import Item, Category

fake = Faker()
User = get_user_model()


def create_items_per_category(user):
    """প্রতি category থেকে ২টা করে item তৈরি করে — already থাকলে skip"""
    categories = Category.objects.all()

    if not categories.exists():
        return

    items_to_create = []
    for category in categories:
        existing = Item.objects.filter(
            user=user,
            category=category
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


@receiver(user_logged_in)
def seed_on_login(sender, request, user, **kwargs):
    create_items_per_category(user)


@receiver(post_save, sender=User)
def seed_on_signup(sender, instance, created, **kwargs):
    if not created:
        return
    create_items_per_category(instance)