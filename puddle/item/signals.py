from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from item.models import Item
from item.seed_helpers import (
    create_items_per_category,
    is_admin_user,
    seed_admin_items,
)

User = get_user_model()

@receiver(post_migrate)
def seed_after_migrate(sender, **kwargs):
    if sender.name != 'item':
        return
    seed_admin_items()

@receiver(post_save, sender=User)
def seed_on_signup(sender, instance, created, **kwargs):
    if not created or is_admin_user(instance):
        return
    if not Item.objects.filter(user=instance).exists():
        create_items_per_category(instance)

@receiver(user_logged_in)
def seed_on_login(sender, request, user, **kwargs):
    if is_admin_user(user):
        return
    if not Item.objects.filter(user=user).exists():
        create_items_per_category(user)