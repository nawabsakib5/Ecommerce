from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ConversationMessage
from core.models import Notification


@receiver(post_save, sender=ConversationMessage)
def notify_on_message(sender, instance, created, **kwargs):
    if not created:
        return

    conversation = instance.conversation
    sender_user = instance.created_by

    # Conversation এর অন্য member কে notification পাঠাবে
    for member in conversation.members.all():
        if member != sender_user:
            # Already আছে কিনা check — duplicate এড়াতে
            already = Notification.objects.filter(
                user=member,
                notification_type='message',
                link=f"/inbox/{conversation.id}/"
            ).exists()

            if not already:
                Notification.objects.create(
                    user=member,
                    title="New Message 💬",
                    message=f"{sender_user.username} sent you a message about '{conversation.item.name}'",
                    notification_type='message',
                    link=f"/inbox/{conversation.id}/",
                )