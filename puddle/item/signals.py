from django.core.cache import cache
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from item.models import Item
from item.seed_helpers import seed_admin_catalog

@receiver(post_migrate)
def seed_after_migrate(sender, **kwargs):
    if sender.name != 'item':
        return
    seed_admin_catalog()

@receiver(post_save, sender=Item)
def clear_category_cache(sender, **kwargs):
    cache.delete('all_categories')