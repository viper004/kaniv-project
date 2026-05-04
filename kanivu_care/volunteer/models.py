from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Volunteer(models.Model):

    BLOOD_GROUP_CHOICES = (
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    )

    BATCH_CHOICES = (
        ("MCA", "MCA"),
        ("BCA", "BCA"),
        ("BSc CS", "BSc CS"),
        ("BCom", "BCom"),
        ("BA","BA"),
        ("BSW","BSW")
    )


    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    age = models.PositiveIntegerField()

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True
    )

    address = models.TextField()
    reason = models.TextField()
    is_approved=models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_volunteers"
    )
    declined=models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)

    # Student fields
    is_student = models.BooleanField(default=False)
    was_student = models.BooleanField(default=False)
    admission_no = models.CharField(max_length=50, blank=True, null=True)
    start_year = models.CharField(max_length=5, blank=True, null=True)
    end_year = models.CharField(max_length=5, blank=True, null=True)
    

    batch = models.CharField(
        max_length=20,
        choices=BATCH_CHOICES,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_student_academic_period_over(self, on_date=None):
        if not self.is_student:
            return False

        if not self.end_year or not str(self.end_year).isdigit():
            return False

        current_date = on_date or timezone.localdate()
        end_year = int(self.end_year)

        if current_date.year > end_year:
            return True

        return current_date.year == end_year and current_date.month >= 4
    
class Campaign(models.Model):

    type_choices = (
        ('Health', 'Health & Medical'),
        ('Social', 'Social Service'),
        ('Environment', 'Environmental'),
        ('Education', 'Educational'),
        ('Fundraising', 'Fundraising'),
        ('Awareness', 'Awareness'),
        ('Event', 'Event-Based'),
        ('Skill', 'Skill-Based'),
    )
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="campaign/", null=True, blank=True)
    description = models.TextField()
    type = models.CharField(
        max_length=50,
        choices=type_choices
        )
    max_volunteers = models.IntegerField(default=0)
    current_volunteers = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    created_on = models.DateTimeField(auto_now_add=True)


class CampaignEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="campaign_enrollments")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="enrollments")
    joined_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "campaign"], name="unique_campaign_enrollment")
        ]



class Volunteer_Notifications(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    send_date = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="volunteer_notifications_sent"
    )

    def __str__(self):
        return self.title
