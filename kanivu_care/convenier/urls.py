from django.urls import path

from convenier import views

app_name="convenier"

urlpatterns=[
    path("create/member/",views.createMember,name="create_member"),
    path("pending_requests/",views.pendingRequests,name="pending_requests"),
    path("request_response/approve/<int:id>/",views.requestApproved,name="approved"),
    path("request_response/reject/<int:id>/",views.requestRejected,name="rejected"),




]