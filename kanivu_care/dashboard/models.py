from django.db import models
from django.contrib.auth.models import User

from members.models import memberRegistration


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
    
class NotifyModelPriority(models.Model):
    PRIORITY_DUTY=(
        ("Finance", "Finance"),
        ("Collection Team", "Collection Team")
    )
    notify=models.ForeignKey(NotifyModel,on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=memberRegistration.DEPARTMENT_CHOICES,null=True,blank=True)
    priority_duty=models.CharField(max_length=20,choices=PRIORITY_DUTY,null=True,blank=True)
    is_readed=models.BooleanField(default=False)
    readed_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    announced_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.notify.title
    
class FinanceModel(models.Model):

    COLLECTION_TYPE_CHOICES=(
        ("Weekly Collection","Weekly Collection"),
        ("Monthly Collection","Monthly Collection"),
        ("Special Collection","Special Collection"),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    collection_type=models.CharField(choices=COLLECTION_TYPE_CHOICES,max_length=100)
    description=models.TextField()
    collection_date=models.DateField()
    announced_date=models.DateField(auto_now_add=True)
    image=models.ImageField(upload_to="finance/")

    def __str__(self):
        return self.user.username
    

class CollectionGalleryModel(models.Model):
    image=models.ImageField(upload_to="collections/")

    def __str__(self):
        return str(self.image)

    

 
class CollectionModel(models.Model):

    COLLECTION_TYPE_CHOICES=(
        ("Weekly Collection","Weekly Collection"),
        ("Event Based Collection","Event Based Collection"),
        ("Special Collection","Special Collection"),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    collection_type=models.CharField(choices=COLLECTION_TYPE_CHOICES,max_length=100)
    description=models.TextField()
    collection_date=models.DateField()
    announced_date=models.DateField(auto_now_add=True)
    total=models.IntegerField()
    is_completed=models.BooleanField(default=False)
    images=models.ManyToManyField(CollectionGalleryModel,blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.collection_type}"
    

    
class KitReceiverModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=30)
    age=models.IntegerField()
    family=models.TextField()
    address=models.TextField()
    location=models.URLField(max_length=255)
    photo=models.ImageField(upload_to="kit/")
    announced_date=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class AnnouncementModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    description=models.TextField()
    video_url=models.URLField(null=True,blank=True)
    thumbnail=models.ImageField(upload_to="announcement/",null=True,blank=True)
    thumbnail_url=models.URLField(null=True,blank=True)
    photo1=models.ImageField(upload_to="announcement/",null=True,blank=True)
    photo2=models.ImageField(upload_to="announcement/",null=True,blank=True)
    event_date=models.DateField()
    announced_date=models.DateTimeField(auto_now_add=True)
    is_completed=models.BooleanField(default=False)
    is_hidden=models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    