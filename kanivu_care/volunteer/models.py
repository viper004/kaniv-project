from django.db import models
from django.contrib.auth.models import User


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
    )

    YEAR_CHOICES = (
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
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

    # Student fields
    is_student = models.BooleanField(default=False)
    admission_no = models.CharField(max_length=50, blank=True, null=True)
    period = models.CharField(max_length=20, blank=True, null=True)

    batch = models.CharField(
        max_length=20,
        choices=BATCH_CHOICES,
        blank=True,
        null=True
    )

    year = models.CharField(
        max_length=20,
        choices=YEAR_CHOICES,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name