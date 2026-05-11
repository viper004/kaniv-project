from django.urls import path
from coordinator import views

app_name="coordinator"

urlpatterns=[
    path("request/create/member/",views.requestMember,name="request_member"),
    path("request/resubmit/member/",views.resubmitRequestMember,name="resubmit_member"),
    path("request/track/member/",views.trackMember,name="track_member"),
    path("delete/record/member/<int:id>/",views.deleteRecord,name="delete_record"),
    path("change_duty/",views.trackMember,name="change_duty"),
    path("events/", views.events_coordinator, name="events_coordinator"),
    path("manage-events/", views.manage_events, name="manage_events"),
    path("approve-event/<int:event_id>/", views.approve_event, name="approve_event"),
    path("reject-event/<int:event_id>/", views.reject_event, name="reject_event"),
    path("reapply-event/<int:event_id>/", views.reapply_event, name="reapply_event"),
    path("faqs/", views.manage_faqs, name="manage_faqs"),
    path("api/get-faqs/", views.get_faqs, name="get_faqs"),
]
