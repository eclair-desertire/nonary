from django.contrib import admin
from location.models import Post, City


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'object_type', 'created_at', 'is_active')
    list_display_links = ('name', 'address', 'object_type', 'created_at', 'is_active')
    search_fields = ('name', 'address')
    list_filter = ('is_active', 'object_type')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'is_active')
    list_display_links = ('name', 'slug', 'created_at', 'is_active')
    search_fields = ('name', )
    list_filter = ('is_active', )
    filter_horizontal = ('storehouses',)

    fieldsets = (
        (None, {'fields': ('name', 'storehouses', )}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at',)
