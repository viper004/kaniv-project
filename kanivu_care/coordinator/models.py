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
        ("1", "1st Year"),
        ("2", "2nd Year"),
        ("3", "3rd Year"),
        ("4", "4th Year"),
    )

    

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adno = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    batch = models.CharField(max_length=10)
    current_year = models.CharField(max_length=5, choices=YEAR_CHOICES)

    def __str__(self):
        return self.user.username