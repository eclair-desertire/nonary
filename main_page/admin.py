from django.contrib import admin
from main_page.models import Story, Stock


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'story_file', 'story_type', 'deadline', 'created_at', 'is_active')
    list_display_links = ('name', 'story_file', 'story_type', 'deadline', 'created_at', 'is_active')
    list_filter = ('is_active', )

    fieldsets = (
        (None, {'fields': ('name', 'is_active', 'story_file', 'link', 'deeplink', 'deadline', 'story_type', 'link_type',
                           'position')}),
        ('Переход в акцию', {'fields': ('stock', )}),
        ('Переход в карточку товара', {'fields': ('product', )}),
        ('Переход в категорию фильтрованую по бренду, типу', {'fields': ('category', 'brand', 'child_category',
                                                                         )}),
        ('Информативный банер', {'fields': ('info', )}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'image', 'deadline', 'created_at', 'is_active')
    list_display_links = ('title', 'short_description', 'image', 'deadline', 'created_at', 'is_active')
    list_filter = ('is_active', )
    filter_horizontal = ('products',)
