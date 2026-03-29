from django.contrib import admin
from .models import Volunteer


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_student', 'is_approved')
    list_filter = ('is_student', 'is_approved')   # 👈 THIS IS KEY
    search_fields = ('name', 'email', 'phone')