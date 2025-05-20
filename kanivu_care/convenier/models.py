from django.db import models
from django.contrib.auth.models import User

from users.models import UserProfile

from members.models import memberRegistration
# Create your models here.


class convinierModel(models.Model):
    convenier=models.ForeignKey(UserProfile,on_delete=models.CASCADE)

    def __str__(self):
        return self.convenier.user.username

class pendingMemberAddRequest(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    isApproved=models.BooleanField(default=False)
    isPending=models.BooleanField(default=False)
    reason=models.CharField(max_length=255,null=True,blank=True)

    
    def __str__(self):
        return self.user.username