from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class memberRegistration(models.Model):

    DEPARTMENT_CHOICES=(
        ("bba","BBA"),
        ("bca","BCA"),
        ("bsc_cs","BSC CS"),
        ("bcom_tax","bcom tax"),
        ("ttm","ttm"),
        ("bcom_ca_and_finance","bcom ca and finance"),
        ("bcom_co-operation","bcom co-operation"),
        ("ba_literature","ba literature"),
        ("ba_communicative_english","ba_communicative_english"),
        ("ba_journalism","ba_journalism"),
        ("electronics","electronics"),
        ("bsw","bsw"),

    )

    YEAR_CHOICES=(
        ("1","1"),
        ("2","2"),
        ("3","3"),
        ("4","4"),

    )


    user=models.OneToOneField(User,on_delete=models.CASCADE)
    adno=models.CharField(max_length=255)
    department=models.CharField(choices=DEPARTMENT_CHOICES)
    batch=models.CharField(max_length=10)
    current_year=models.CharField(choices=YEAR_CHOICES,max_length=5)

    def __str__(self):
        return self.user.username
    