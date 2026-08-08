from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Item

User = get_user_model()


@receiver(post_save, sender=Item)
def clear_category_cache(sender, **kwargs):
    cache.delete('all_categories')


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
                message=f"Your item '{instance.name}' has been marked as sold.",
                notification_type='sale',
                link=f"/items/{instance.id}/",
            )