from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class NotifyModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    description=models.TextField()
    is_completed=models.BooleanField(default=False)
    program_date=models.DateField(auto_now_add=False)
    announced_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.title}"