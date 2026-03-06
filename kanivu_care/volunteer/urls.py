from django.urls import path
from . import views

app_name = "volunteer"

urlpatterns = [
    path('join/', views.join_volunteer, name='join_volunteer'),
]
