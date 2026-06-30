from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django.contrib.admin.sites import AdminSite
from .admin import PlainTextUserAdmin

from .models import Message


class OneToOneChatViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.alice = User.objects.create_user(username='alice', password='password123')
        self.bob = User.objects.create_user(username='bob', password='password123')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_accepts_plain_text_password(self):
        User = get_user_model()
        user = User.objects.create_user(username='plainuser', password='plainpass')

        response = self.client.post(reverse('login'), {'username': 'plainuser', 'password': 'plainpass'})

        self.assertRedirects(response, reverse('one_to_one_chat'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_view_renders_chat_for_two_users(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse('one_to_one_chat'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'One-to-One Chat')
        self.assertContains(response, self.alice.username)
        self.assertContains(response, self.bob.username)

    def test_send_message_endpoint_creates_message_and_returns_json(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse('send_message'),
            {'content': 'hello there'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().content, 'hello there')
        self.assertEqual(Message.objects.first().sender, self.alice)
        self.assertEqual(Message.objects.first().receiver, self.bob)

    def test_send_message_uses_logged_in_user_as_sender(self):
        self.client.force_login(self.bob)
        response = self.client.post(
            reverse('send_message'),
            {'content': 'from bob'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().sender, self.bob)
        self.assertEqual(Message.objects.first().receiver, self.alice)

    def test_poll_endpoint_returns_only_new_messages(self):
        self.client.force_login(self.alice)
        existing = Message.objects.create(sender=self.alice, receiver=self.bob, content='first message')

        response = self.client.get(reverse('poll_messages'), {'after_id': existing.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['messages'], [])

    def test_admin_form_shows_plain_text_password_for_demo_users(self):
        admin_site = AdminSite()
        admin = PlainTextUserAdmin(get_user_model(), admin_site)
        form = admin.get_form(None, obj=self.alice)()

        self.assertEqual(form.fields['password'].initial, 'password123')
        self.assertEqual(form.fields['password'].widget.attrs['readonly'], 'readonly')
