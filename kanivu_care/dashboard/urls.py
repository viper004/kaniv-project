from django.urls import path

from dashboard import views

app_name="dashboard"

urlpatterns=[
    path("",views.Dashboard,name="dashboard"),
    path("notification",views.Notification,name="notification"),
    path("notification/delete/<int:id>/",views.deleteNotification,name="delete_notification"),
    path("notification/end/<int:id>/",views.endNotify,name="end_notification"),
    path("finance",views.Finance,name="finance"),
    path("delete_finance/<int:id>/",views.deleteFinance,name="delete_finance")
]