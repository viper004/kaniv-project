from django.urls import path

from convenier import views

app_name="convenier"

urlpatterns=[
    path("",views.Convenier,name="convenier"),
    path("create/coordinator",views.createCoordinator,name="create_coordinator"),
    path("change_role",views.changeRole,name="change_role"),

]