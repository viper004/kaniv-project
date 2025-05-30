from django.urls import path
from coordinator import views

from convenier.views import changeDuty

app_name="coordinator"

urlpatterns=[
    path("request/create/member/",views.requestMember,name="request_member"),
    path("request/resubmit/member/",views.resubmitRequestMember,name="resubmit_member"),
    path("request/track/member/",views.trackMember,name="track_member"),
    path("delete/record/member/<int:id>/",views.deleteRecord,name="delete_record"),
    path("change_duty/",views.trackMember,name="change_duty"),

]