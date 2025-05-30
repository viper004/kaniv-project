from django.urls import path

from convenier import views

app_name="convenier"

urlpatterns=[
    path("",views.Convenier,name="convenier"),
    path("create/member/",views.createMember,name="create_member"),
    path("change_role/",views.changeRole,name="change_role"),
    path("change_role/promote/<int:id>/",views.promoteUser,name="promote"),
    path("change_role/demote/<int:id>/",views.demoteUser,name="demote"),
    path("change_duty/",views.changeDuty,name="change_duty"),
    path("kick_member/",views.kickMember,name="kick_member"),
    path("pending_requests/",views.pendingRequests,name="pending_requests"),
    path("request_response/approve/<int:id>/",views.requestApproved,name="approved"),
    path("request_response/reject/<int:id>/",views.requestRejected,name="rejected"),




]