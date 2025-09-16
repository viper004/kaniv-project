from django.contrib import admin

from dashboard.models import NotifyModel,FinanceModel,AnnouncementModel

admin.site.register(NotifyModel)
admin.site.register(FinanceModel)
admin.site.register(AnnouncementModel)


# Register your models here.
