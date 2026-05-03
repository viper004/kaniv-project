from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include("web.urls",namespace="web")),
    path('', include('members.urls')),
    path("users/",include("users.urls",namespace="users")),
    path("convenier/",include("convenier.urls",namespace="convenier")),
    path("coordinator/",include("coordinator.urls",namespace="coordinator")),
    path("dashboard/",include("dashboard.urls",namespace="dashboard")),
    path("volunteer/",include("volunteer.urls",namespace="volunteer")),
    path("officials/", include("officials.urls", namespace="officials")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
