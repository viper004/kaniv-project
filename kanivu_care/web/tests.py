from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.models import SosMessages
from users.models import UserProfile
from volunteer.models import Volunteer


class HomeVolunteerCtaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="secret123",
            email="tester@example.com",
        )
        UserProfile.objects.create(user=self.user, role="public_user")

    def test_home_shows_join_button_when_user_has_no_volunteer_record(self):
        self.client.login(username="tester", password="secret123")

        response = self.client.get(reverse("web:home"))

        self.assertContains(response, "Join Kanivu")
        self.assertNotContains(response, reverse("dashboard:volunteer_dashboard"))

    def test_home_shows_dashboard_for_approved_volunteer(self):
        Volunteer.objects.create(
            user=self.user,
            name="Tester",
            email="tester@example.com",
            phone="9876543210",
            age=24,
            address="Address",
            reason="Helping others",
            is_approved=True,
        )
        self.client.login(username="tester", password="secret123")

        response = self.client.get(reverse("web:home"))

        self.assertContains(response, reverse("dashboard:volunteer_dashboard"))
        self.assertNotContains(response, "Join Kanivu")

    def test_home_shows_join_button_again_after_volunteer_is_removed(self):
        volunteer = Volunteer.objects.create(
            user=self.user,
            name="Tester",
            email="tester@example.com",
            phone="9876543210",
            age=24,
            address="Address",
            reason="Helping others",
            is_approved=True,
        )
        volunteer.delete()
        self.client.login(username="tester", password="secret123")

        response = self.client.get(reverse("web:home"))

        self.assertContains(response, "Join Kanivu")
        self.assertNotContains(response, reverse("dashboard:volunteer_dashboard"))

    def test_logged_out_sos_button_redirects_to_login_without_modal(self):
        response = self.client.get(reverse("web:home"))

        self.assertContains(response, reverse("users:login"))
        self.assertNotContains(response, 'id="sosModal"')

    def test_logged_in_home_shows_newest_sos_messages_in_modal(self):
        older = SosMessages.objects.create(
            user=self.user,
            contact="1111111111",
            title="Older SOS",
            message="Older emergency details",
        )
        newest = SosMessages.objects.create(
            user=self.user,
            contact="2222222222",
            title="Newest SOS",
            message="Newest emergency details",
        )
        SosMessages.objects.filter(id=older.id).update(
            created_at=timezone.now() - timezone.timedelta(hours=1)
        )
        SosMessages.objects.filter(id=newest.id).update(
            created_at=timezone.now()
        )
        self.client.login(username="tester", password="secret123")

        response = self.client.get(reverse("web:home"))
        content = response.content.decode()

        self.assertContains(response, 'id="sosModal"')
        self.assertContains(response, "SOS Messages")
        self.assertContains(response, "Send SOS")
        self.assertContains(response, "Newest SOS")
        self.assertContains(response, "Older SOS")
        self.assertContains(response, "Sent by tester")
        self.assertContains(response, 'data-contact="2222222222"')
        self.assertContains(response, 'data-message="Newest emergency details"')
        self.assertLess(content.index("Newest SOS"), content.index("Older SOS"))
