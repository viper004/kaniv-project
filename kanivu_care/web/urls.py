from django.urls import path

from web.views import Home

app_name="web"

urlpatterns=[
    path("",Home,name="home")
]