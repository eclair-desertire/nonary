from django.contrib import admin
from app_filter.models import (
    CategoryFilter
)


@admin.register(CategoryFilter)
class CategoryFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'property', 'is_active')
    list_display_links = ('name', 'category', 'property', 'is_active')
    list_filter = ('is_active', 'category', 'property')
    search_fields = ('name', )

    fieldsets = (
        (None, {'fields': ('name', 'property', 'category', 'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)

