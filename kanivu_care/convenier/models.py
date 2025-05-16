from django.db import models

from users.models import UserProfile
# Create your models here.


class convinierModel(models.Model):
    convenier=models.ForeignKey(UserProfile,on_delete=models.CASCADE)

    def __str__(self):
        return self.convenier.user.username
