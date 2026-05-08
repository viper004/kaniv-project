from django.contrib import admin
from .models import ReportRequest, FundRequest

@admin.register(ReportRequest)
class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requested_by', 'requested_to_role', 'is_completed', 'requested_at')
    list_filter = ('is_completed', 'requested_to_role')
    search_fields = ('title', 'description')

@admin.register(FundRequest)
class FundRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted_by', 'amount', 'status', 'submitted_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
