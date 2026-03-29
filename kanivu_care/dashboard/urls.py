from django.urls import path

from dashboard import views

app_name="dashboard"

urlpatterns=[
    path("",views.Dashboard,name="dashboard"),
    path("notification/",views.Notification,name="notification"),
    path("notification/delete/<int:id>/",views.deleteNotification,name="delete_notification"),
    path("notification/end/<int:id>/",views.endNotify,name="end_notification"),
    path("announcement/",views.Announcement,name="announcement"),
    path("announcement/update_announcement/",views.updateAnnouncement,name="update_announcement"),
    path("finance/",views.Finance,name="finance"),
    path("finance_notification/",views.financeNotification,name="finance_notification"),
    path("delete_finance/<int:id>/",views.deleteFinance,name="delete_finance"),
    path("kit_receivers/",views.kitReceivers,name="kit_receivers"),
    path("update_kit/",views.updateKit,name="update_kit"),
    path("delete_kit/<int:id>/",views.deleteKit,name="delete_kit"),
    path("manage_members/",views.manageMembers,name="manage_members"),
    path("manage_members/promote/<int:id>/",views.promoteUser,name="promote"),
    path("manage_members/demote/<int:id>/",views.demoteUser,name="demote"),
    path("change_duty/",views.changeDuty,name="change_duty"),
    path("kick_member/",views.kickMember,name="kick_member"),
    path("collection_team/",views.collectionTeam,name="collection_team"),
    path("update_collection_team/",views.updateCollectionTeam,name="update_collection_team"),
    path("collection_team_notification/",views.collectionTeamNotification,name="collection_team_notification"),
    path("donations/",views.donations,name="donations"),
    path("donations/<str:id>/",views.viewDonation,name="view_donation"),
    path("approve_volunteers/",views.approve_volunteers,name="approve_volunteers"),
    path("approve-volunteer/", views.approve_volunteer, name="approve_volunteer"),
    path("reject-volunteer/", views.reject_volunteer, name="reject_volunteer"),
    path("manage_volunteers/", views.manage_volunteers, name="manage_volunteers"),
    path("remove_volunteer/", views.remove_volunteer, name="remove_volunteer"),
    path("volunteer_dashboard/",views.volunteer_dashboard,name="volunteer_dashboard"),




]