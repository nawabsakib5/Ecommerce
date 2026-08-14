import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        # Authentication check
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Authorization check — user এই conversation এর member কিনা
        is_member = await self.check_membership()
        if not is_member:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()

        # Empty message reject
        if not message:
            return

        # Message length limit — max 1000 characters
        if len(message) > 1000:
            return

        msg_obj = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'sender_id': self.user.id,
                'timestamp': msg_obj.created_at.strftime('%I:%M %p'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def check_membership(self):
        """User এই conversation এর member কিনা check করো"""
        from .models import Conversation
        return Conversation.objects.filter(
            id=self.conversation_id,
            members=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, content):
        from .models import Conversation, ConversationMessage
        conversation = Conversation.objects.get(id=self.conversation_id)
        return ConversationMessage.objects.create(
            conversation=conversation,
            content=content,
            created_by=self.user,
        )