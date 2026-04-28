from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class memberRegistration(models.Model):
    DEPARTMENT_CHOICES = (
        ("bba", "BBA"),
        ("bca", "BCA"),
        ("bsc_cs", "BSc CS"),
        ("bcom_tax", "BCom Tax"),
        ("ttm", "TTM"),
        ("bcom_ca_and_finance", "BCom CA and Finance"),
        ("bcom_co_operation", "BCom Co-operation"),
        ("ba_literature", "BA Literature"),
        ("ba_communicative_english", "BA Communicative English"),
        ("ba_journalism", "BA Journalism"),
        ("electronics", "Electronics"),
        ("bsw", "BSW"),
    )

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    DUTY_CHOICES = (
        ("No Duty", "No Duty"),
        ("Finance", "Finance"),
        ("Collection Team", "Collection Team"),
        ("Event Organizers", "Event Organizers"),  # Fixed typo
        ("Team Controller", "Team Controller"),
    )

    MEMBERSHIP_STATUS_CHOICES = (
        ("active", "Active"),
        ("volunteer", "Moved to Volunteer"),
        ("inactive", "Inactive"),
    )

    

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="memberregistration")
    adno = models.CharField(max_length=255, blank=True, default="")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, default="")
    start_year = models.CharField(max_length=5, blank=True, default="")
    end_year = models.CharField(max_length=5, blank=True, default="")
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        default="",
    )
    duty = models.CharField(max_length=50, choices=DUTY_CHOICES, default="No Duty")
    membership_status = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default="active",
    )
    membership_decided_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def is_profile_complete(self):
        required_fields = [
            self.adno,
            self.department,
            self.start_year,
            self.end_year,
            self.blood_group,
        ]
        return all(str(value).strip() for value in required_fields)

    def is_membership_expired(self, on_date=None):
        if self.membership_status != "active":
            return False

        if not self.end_year or not str(self.end_year).isdigit():
            return False

        current_date = on_date or timezone.localdate()
        end_year = int(self.end_year)

        if current_date.year > end_year:
            return True

        return current_date.year == end_year and current_date.month >= 4

