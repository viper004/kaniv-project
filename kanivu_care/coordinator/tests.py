from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from coordinator.models import Event
from users.models import UserProfile


class EventReapplyTests(TestCase):
    def setUp(self):
        self.convenier = User.objects.create_user(username="convener", password="testpass123")
        UserProfile.objects.update_or_create(
            user=self.convenier,
            defaults={"role": "convenier"},
        )

        self.principal = User.objects.create_user(username="principal", password="testpass123")
        UserProfile.objects.update_or_create(
            user=self.principal,
            defaults={"role": "principal"},
        )

        self.event = Event.objects.create(
            title="Old title",
            description="Old description",
            event_date="2026-05-20",
            applied_by=self.convenier,
            status="REJECTED_TO_CONVENER",
            rejection_reason="Need more details",
            rejected_by=self.principal,
        )

    def test_convener_can_edit_and_reapply_rejected_event(self):
        self.client.login(username="convener", password="testpass123")

        response = self.client.post(
            reverse("coordinator:reapply_event", args=[self.event.id]),
            {
                "title": "Updated title",
                "description": "Updated description",
                "event_date": "2026-05-25",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Updated title")
        self.assertEqual(self.event.description, "Updated description")
        self.assertEqual(str(self.event.event_date), "2026-05-25")
        self.assertEqual(self.event.status, "PENDING_PRINCIPAL")
        self.assertEqual(self.event.rejection_reason, "")
        self.assertIsNone(self.event.rejected_by)

    def test_convener_cannot_directly_approve_returned_rejected_event(self):
        self.client.login(username="convener", password="testpass123")

        response = self.client.post(
            reverse("coordinator:approve_event", args=[self.event.id]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"status": "error", "message": "Unauthorized or invalid state"},
        )

        self.event.refresh_from_db()
        self.assertEqual(self.event.status, "REJECTED_TO_CONVENER")
