from django.db import models
from django.conf import settings
from item.models import Item


class Conversation(models.Model):
    item = models.ForeignKey(Item, related_name='conversations', on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified_at',)

    def __str__(self):
        return f"Conversation about {self.item.name}"

    def get_other_member(self, user):
        return self.members.exclude(id=user.id).first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(created_by=user).count()


class ConversationMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_messages',
        on_delete=models.CASCADE
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"{self.created_by.username}: {self.content[:50]}"