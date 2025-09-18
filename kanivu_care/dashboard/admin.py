from django.contrib import admin

from dashboard.models import NotifyModel,FinanceModel,AnnouncementModel,NotifyModelPriority

admin.site.register(NotifyModel)
admin.site.register(FinanceModel)
admin.site.register(AnnouncementModel)
admin.site.register(NotifyModelPriority)



# Register your models here.
