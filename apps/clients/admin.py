from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'email', 'created_at']
    search_fields = ['full_name', 'phone', 'email']
    ordering = ['full_name']