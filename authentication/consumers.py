import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        print(f"Connecting to room: {self.room_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting from room: {self.room_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Received data: {text_data}")
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action', 'message')
        message = text_data_json.get('message')
        team_name = text_data_json.get('team_name', 'Anonymous')

        if action == 'message':
            await self.save_message(self.room_name, message, team_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'team_name': team_name,
                }
            )
        elif action == 'like':
            message_id = text_data_json['message_id']
            await self.like_message(message_id)
            message = await self.get_message(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_likes_dislikes',
                    'message_id': message_id,
                    'likes': message.likes,
                    'dislikes': message.dislikes,
                }
            )
        elif action == 'dislike':
            message_id = text_data_json['message_id']
            await self.dislike_message(message_id)
            message = await self.get_message(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_likes_dislikes',
                    'message_id': message_id,
                    'likes': message.likes,
                    'dislikes': message.dislikes,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        team_name = event['team_name']
        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': message,
            'team_name': team_name,
        }))

    async def update_likes_dislikes(self, event):
        message_id = event['message_id']
        likes = event['likes']
        dislikes = event['dislikes']
        await self.send(text_data=json.dumps({
            'action': 'update_likes_dislikes',
            'message_id': message_id,
            'likes': likes,
            'dislikes': dislikes,
        }))

    @database_sync_to_async
    def save_message(self, room_name, message, team_name):
        ChatMessage.objects.create(room_name=room_name, message=message, team_name=team_name, likes=0, dislikes=0)

    @database_sync_to_async
    def like_message(self, message_id):
        message = ChatMessage.objects.get(id=message_id)
        message.likes += 1
        message.save()

    @database_sync_to_async
    def dislike_message(self, message_id):
        message = ChatMessage.objects.get(id=message_id)
        message.dislikes += 1
        message.save()

    @database_sync_to_async
    def get_message(self, message_id):
        return ChatMessage.objects.get(id=message_id)





