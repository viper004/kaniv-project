from django.contrib import admin
from django.urls import path,include



urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include("web.urls",namespace="web")),
    path("users/",include("users.urls",namespace="users")),
    path("convenier/",include("convenier.urls",namespace="convenier")),
    path("coordinator/",include("coordinator.urls",namespace="coordinator")),
    path("dashboard/",include("dashboard.urls",namespace="dashboard")),
]
