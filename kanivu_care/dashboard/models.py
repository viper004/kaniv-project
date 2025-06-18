from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class NotifyModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    description=models.TextField()
    is_completed=models.BooleanField(default=False)
    program_date=models.DateField()
    announced_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.title}"
    
class FinanceModel(models.Model):

    COLLECTION_TYPE_CHOICES=(
        ("Weekly Collection","Weekly Collection"),
        ("Monthly Collection","Monthly Collection"),
        ("Special Collection","Special Collection"),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    collection_type=models.CharField(choices=COLLECTION_TYPE_CHOICES)
    description=models.TextField()
    collection_date=models.DateField()
    announced_date=models.DateField(auto_now_add=True)
    image=models.ImageField(upload_to="media/finance/")

    def __str__(self):
        return self.user.username
    