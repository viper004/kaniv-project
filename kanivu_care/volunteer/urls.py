from django.urls import path
from . import views

app_name = "volunteer"

urlpatterns = [
    path('join/', views.join_volunteer, name='join_volunteer'),
    path('dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('campaign/new/', views.new_campaign, name='new_campaign'),
    path('campaign/enroll/<int:id>/', views.enroll_campaign, name='enroll_campaign'),
    path('campaign/unenroll/<int:id>/', views.unenroll_campaign, name='unenroll_campaign'),
    path('campaign/delete/<int:id>/', views.delete_campaign, name='delete_campaign'),
]
