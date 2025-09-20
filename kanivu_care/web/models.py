from django.db import models

# Create your models here.

class DonationModel(models.Model):
    user=models.ForeignKey("auth.User",on_delete=models.CASCADE)
    full_name=models.CharField(max_length=30)
    email=models.EmailField()
    phone_number=models.CharField(max_length=10)
    amount=models.CharField(max_length=7)
    card_no=models.CharField(max_length=16)
    name_on_card=models.CharField()
    expiry_date=models.CharField()
    cvv=models.CharField(max_length=3)
    note=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.user.username
