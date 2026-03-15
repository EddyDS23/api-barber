from django.contrib import admin
from .models import GalleryCategory, Gallery


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'display_order']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Auto-genera el slug desde el nombre


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'barber', 'display_order', 'is_active']
    list_filter = ['category', 'is_active', 'barber']
    search_fields = ['title']