from django.contrib import admin

from dashboard.models import NotifyModel,FinanceModel,AnnouncementModel,NotifyModelPriority,CollectionModel,CollectionGalleryModel

admin.site.register(NotifyModel)
admin.site.register(FinanceModel)
admin.site.register(AnnouncementModel)
admin.site.register(NotifyModelPriority)
admin.site.register(CollectionModel)
admin.site.register(CollectionGalleryModel)





# Register your models here.
