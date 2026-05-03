from django.urls import path

from officials.views import index

app_name = "officials"

urlpatterns = [
    path("", index, name="index"),
]

