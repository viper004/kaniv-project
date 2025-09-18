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
    path("collection_team_notification/",views.collectionTeamNotification,name="collection_team_notification"),


]