from django.db import models
from django.contrib.auth.models import User


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

    YEAR_CHOICES = (
        ("First Year", "First Year"),
        ("Second Year", "Second Year"),
        ("Third Year", "Third Year"),
        ("Fourth Year", "Fourth Year"),
    )

    DUTY_CHOICES = (
        ("No Duty", "No Duty"),
        ("Finance", "Finance"),
        ("Collection Team", "Collection Team"),
        ("Event Organizers", "Event Organizers"),  # Fixed typo
        ("Team Controller", "Team Controller"),
    )

    

    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="memberregistration")
    adno = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    batch = models.CharField(max_length=10)
    current_year = models.CharField(max_length=15, choices=YEAR_CHOICES)
    duty = models.CharField(max_length=50, choices=DUTY_CHOICES, default="No Duty")

    def __str__(self):
        return self.user.username
    

