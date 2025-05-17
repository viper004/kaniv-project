from django.urls import path

from convenier import views

app_name="convenier"

urlpatterns=[
    path("",views.Convenier,name="convenier"),
    path("create/coordinator",views.createCoordinator,name="create_coordinator"),
    path("change_role",views.changeRole,name="change_role"),
    path("change_role/promote/<int:id>/",views.promoteUser,name="promote"),
    path("change_role/demote/<int:id>/",views.demoteUser,name="demote"),


]