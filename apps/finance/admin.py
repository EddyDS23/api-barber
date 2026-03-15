from django.contrib import admin
from .models import TypeTransaction, CategoryTransaction, FinancialTransaction


@admin.register(TypeTransaction)
class TypeTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']


@admin.register(CategoryTransaction)
class CategoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'concept', 'amount', 'type', 'category', 'date']
    list_filter = ['type', 'category', 'date']
    search_fields = ['concept']
    ordering = ['-date']