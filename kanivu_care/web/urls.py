from django.urls import path

from web.views import Home,donation

app_name="web"

urlpatterns=[
    path("",Home,name="home"),
    path("donation/",donation,name="donation")

]