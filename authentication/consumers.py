import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatMessage, MessageReaction
import re

import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    with open('badwords.txt') as f:  
        BAD_WORDS = [line.strip() for line in f]
    async def connect(self):
        print("Room name:", self.scope['url_route']['kwargs'].get('room_name'))
        print("League number:", self.scope['url_route']['kwargs'].get('league_number'))
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.league_number = self.scope['url_route']['kwargs']['league_number']
        self.room_group_name = f'chat_{self.room_name}_{self.league_number}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        logger.info(f"Connecting to room: {self.room_group_name}")
        print(f"Connecting to room: {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def contains_forbidden_words(self, message):
        pattern = r'\b(?:' + '|'.join(ChatConsumer.BAD_WORDS) + r')\b'
        return re.search(pattern, message, re.IGNORECASE)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        message_id = data.get('message_id')
        message = data.get('message', '')
        team_name = data.get('team_name')

        if action == 'message' and message:
            if await self.contains_forbidden_words(message):
                # Reject the message
                await self.send(text_data=json.dumps({
                    'action': 'error',
                    'message': 'Your message contains inappropriate content.'
                }))
                return
            # Save the new message
            chat_message = await self.save_message(self.room_name, self.league_number, message, team_name)
            
            # Broadcast the new message to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': chat_message.message,
                    'team_name': chat_message.team_name,
                    'timestamp': chat_message.timestamp.isoformat(),
                    'id': chat_message.id,
                    'likes': chat_message.likes_count,
                    'dislikes': chat_message.dislikes_count
                }
            )
        elif action == 'like' and message_id:
            await self.handle_like(message_id, self.scope['user'])
            await self.broadcast_likes_dislikes(message_id)
        elif action == 'dislike' and message_id:
            await self.handle_dislike(message_id, self.scope['user'])
            await self.broadcast_likes_dislikes(message_id)

    async def chat_message(self, event):
        """ Handle broadcasting a new chat message """
        await self.send(text_data=json.dumps({
            'action': 'chat_message',
            'message': event['message'],
            'team_name': event['team_name'],
            'timestamp': event['timestamp'],
            'id': event['id'],
            'likes': event['likes'],
            'dislikes': event['dislikes']
        }))

    async def update_likes_dislikes(self, event):
        """ Handle updating likes/dislikes for a specific message """
        await self.send(text_data=json.dumps({
            'action': 'update_likes_dislikes',
            'message_id': event['message_id'],
            'likes': event['likes'],
            'dislikes': event['dislikes']
        }))

    @database_sync_to_async
    def save_message(self, room_name, league_number, message, team_name):
        """ Save a new chat message to the database """
        return ChatMessage.objects.create(
            room_name=room_name,
            league_number = league_number,
            message=message,
            team_name=team_name,
            likes_count=0,
            dislikes_count=0
        )

    @database_sync_to_async
    def handle_like(self, message_id, user):
        """ Handle toggling like for a message """
        try:
            print(f"Processing LIKE action - Message ID: {message_id}, User: {user}")
            message = ChatMessage.objects.get(id=message_id)
            reaction, created = MessageReaction.objects.get_or_create(
                user=user, 
                message=message,
                defaults={'reaction_type': 'like'})

            if created:
                print(f"Created new reaction for user {user} and message {message_id}. Reaction: LIKE")
                reaction.reaction_type = 'like'
                reaction.save()
                message.likes_count += 1
            else:
                print(f"Existing reaction found for user {user} and message {message_id}. Reaction type: {reaction.reaction_type}")
                if reaction.reaction_type == 'like':
                    reaction.delete()
                    print(f"Deleted LIKE reaction for user {user} and message {message_id}")
                    message.likes_count -= 1
                else:
                    reaction.reaction_type = 'like'
                    reaction.save()
                    print(f"Changed reaction to LIKE for user {user} and message {message_id}")
                    message.likes_count += 1
                    message.dislikes_count -= 1

            # Ensure counts are non-negative
            message.likes_count = max(0, message.likes_count)
            message.dislikes_count = max(0, message.dislikes_count)
            message.save()
            print(f"Updated message like count: {message.likes_count}, dislike count: {message.dislikes_count}")
        except Exception as e:
            print(f"Error handling like action: {e}")

    @database_sync_to_async
    def handle_dislike(self, message_id, user):
        """ Handle toggling dislike for a message """
        try:
            print(f"Processing DISLIKE action - Message ID: {message_id}, User: {user}")
            message = ChatMessage.objects.get(id=message_id)
            reaction, created = MessageReaction.objects.get_or_create(user=user, message=message, defaults={'reaction_type': 'dislike'})

            if created:
                print(f"Created new reaction for user {user} and message {message_id}. Reaction: DISLIKE")
                reaction.reaction_type = 'dislike'
                reaction.save()
                message.dislikes_count += 1
            else:
                print(f"Existing reaction found for user {user} and message {message_id}. Reaction type: {reaction.reaction_type}")
                if reaction.reaction_type == 'dislike':
                    reaction.delete()
                    print(f"Deleted DISLIKE reaction for user {user} and message {message_id}")
                    message.dislikes_count -= 1
                else:
                    reaction.reaction_type = 'dislike'
                    reaction.save()
                    print(f"Changed reaction to DISLIKE for user {user} and message {message_id}")
                    message.dislikes_count += 1
                    message.likes_count -= 1

            # Ensure counts are non-negative
            message.likes_count = max(0, message.likes_count)
            message.dislikes_count = max(0, message.dislikes_count)
            message.save()
            print(f"Updated message like count: {message.likes_count}, dislike count: {message.dislikes_count}")
        except Exception as e:
            print(f"Error handling dislike action: {e}")

    @database_sync_to_async
    def get_message(self, message_id):
        """ Retrieve a message by ID """
        return ChatMessage.objects.get(id=message_id)

    async def broadcast_likes_dislikes(self, message_id):
        """ Broadcast updated likes/dislikes counts """
        message = await self.get_message(message_id)
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_likes_dislikes',
                    'message_id': message_id,
                    'likes': message.likes_count,
                    'dislikes': message.dislikes_count
                }
            )