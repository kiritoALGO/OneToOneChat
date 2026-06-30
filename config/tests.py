from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class OneToOneChatViewTests(TestCase):
    def test_view_renders_chat_for_two_users(self):
        alice = User.objects.create_user(username='alice', password='password123')
        bob = User.objects.create_user(username='bob', password='password123')

        response = self.client.get(reverse('one_to_one_chat'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'One-to-One Chat')
        self.assertContains(response, alice.username)
        self.assertContains(response, bob.username)
