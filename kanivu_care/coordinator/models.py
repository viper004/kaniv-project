from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class coordinateRegistration(models.Model):

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


    

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adno = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    batch = models.CharField(max_length=10)
    current_year = models.CharField(max_length=15, choices=YEAR_CHOICES)

    def __str__(self):
        return self.user.username

class Event(models.Model):
    STATUS_CHOICES = [
        ('PENDING_CONVENER', 'Pending Convener Approval'),
        ('PENDING_PRINCIPAL', 'Pending Principal Approval'),
        ('PENDING_CHAIRMAN', 'Pending Chairman Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED_TO_CONVENER', 'Rejected to Convener'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    applied_by = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING_CONVENER')

    def __str__(self):
        return self.title