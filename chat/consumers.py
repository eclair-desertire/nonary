import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    room_name = ''
    room_group_name = ''

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name
        # if 'client_global_' in self.room_group_name:
        #     client_id = self.room_group_name.split('_')[-1]
        #     User.objects.filter(id=client_id).update(is_online=True)
        user = self.scope.get('user')
        if user and user.is_authenticated:
            user.is_online = True
            await sync_to_async(user.save)()
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        user = self.scope.get('user')
        if user and user.is_authenticated:
            user.is_online = False
            await sync_to_async(user.save)()

        # if 'client_global_' in self.room_group_name:
        #     client_id = self.room_group_name.split('_')[-1]
        #     User.objects.filter(id=client_id).update(is_online=False)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
