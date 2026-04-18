from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dashboard.models import SosMessages
from users.models import UserProfile


class SosMessageViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="sosuser",
            password="secret123",
            first_name="SOS",
            last_name="User",
        )
        UserProfile.objects.create(
            user=self.user,
            role="public_user",
            phone_number="9876543210",
        )
        self.url = reverse("dashboard:sos_message")

    def test_login_required_to_submit_sos_message(self):
        response = self.client.post(self.url, {
            "contact": "9876543210",
            "title": "Need help",
            "message": "Emergency details",
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])
        self.assertEqual(SosMessages.objects.count(), 0)

    def test_authenticated_user_can_submit_sos_message(self):
        self.client.login(username="sosuser", password="secret123")

        response = self.client.post(self.url, {
            "contact": "9876543210",
            "title": "Need help",
            "message": "Emergency details",
        })

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["sos"]["title"], "Need help")
        self.assertEqual(payload["sos"]["sender"], "SOS User")

        sos = SosMessages.objects.get()
        self.assertEqual(sos.user, self.user)
        self.assertEqual(sos.contact, "9876543210")
        self.assertEqual(sos.title, "Need help")
        self.assertEqual(sos.message, "Emergency details")

    def test_submit_sos_message_requires_all_fields(self):
        self.client.login(username="sosuser", password="secret123")

        response = self.client.post(self.url, {
            "contact": "",
            "title": "Need help",
            "message": "Emergency details",
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(SosMessages.objects.count(), 0)
