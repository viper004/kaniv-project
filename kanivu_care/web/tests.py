from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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

        self.assertContains(response, reverse("volunteer:join_volunteer"))
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
        self.assertNotContains(response, reverse("volunteer:join_volunteer"))

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

        self.assertContains(response, reverse("volunteer:join_volunteer"))
        self.assertNotContains(response, reverse("dashboard:volunteer_dashboard"))
