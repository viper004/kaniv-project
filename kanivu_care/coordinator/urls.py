from django.urls import path
from coordinator import views

app_name="coordinator"

urlpatterns=[
    path("request/create/member/",views.requestMember,name="request_member"),
    path("request/resubmit/member/<int:id>/",views.resubmitRequestMember,name="resubmit_member"),
    path("request/track/member/",views.trackMember,name="track_member"),
]