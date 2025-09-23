from django.urls import path

from web.views import Home,donation, myDonations, viewMyDonation

app_name="web"

urlpatterns=[
    path("",Home,name="home"),
    path("donation/",donation,name="donation"),
    path("my_donations/",myDonations,name="my_donations"),
    path("view_my_donation/<str:transaction_id>/",viewMyDonation,name="view_my_donation"),

]