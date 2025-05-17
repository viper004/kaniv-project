from django.urls import path
from coordinator import views

app_name="coordinator"

urlpatterns=[
    path("request/create/member/",views.requestMember,name="request_member")
]