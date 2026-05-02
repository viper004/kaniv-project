from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "members"



urlpatterns = [
    path('blood_donors',views.blood_donors,name='blood_donors'),
]