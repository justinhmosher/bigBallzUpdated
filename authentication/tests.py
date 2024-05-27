# tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ChatMessage

class ChatMessageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.message = ChatMessage.objects.create(
            room_name='testroom',
            message='Hello, world!',
            team_name='Team'
        )

    def test_like_message(self):
        response = self.client.post(f'/like_message/{self.message.id}/')
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.likes, 1)

    def test_dislike_message(self):
        response = self.client.post(f'/dislike_message/{self.message.id}/')
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertEqual(self.message.dislikes, 1)

