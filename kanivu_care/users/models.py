from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    GENDER_CHOICE=(
        ("","Select the gender"),
        ("male","male"),
        ("female","female"),

    )

    ROLE_CHOICE=(
        ("public_user","public_user"),
        ("member","member"),
        ("coordinator","coordinator"),
        ("convenier","convenier"),
    )

    BLOOD_GROUP_CHOICES = [
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=10,null=True,blank=True)
    role=models.CharField(max_length=20,choices=ROLE_CHOICE,default="public_user")
    gender=models.CharField(max_length=10,choices=GENDER_CHOICE,null=True,blank=True)
    address=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    photo=models.ImageField(upload_to="profile_pics/",null=True,blank=True)
    blood=models.CharField(max_length=3,default="",choices=BLOOD_GROUP_CHOICES)
    is_donor = models.BooleanField(default=False)
    


    def __str__(self):
        return self.user.username
    

