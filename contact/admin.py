from django.contrib import admin
from contact.models import Contact, PublicOffer, AboutImage, About, Magazine, Requisite
# from django_summernote.admin import SummernoteModelAdmin


class AboutImageTabular(admin.TabularInline):
    model = AboutImage


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'link_type', 'link', 'created_at', 'is_active')
    list_display_links = ('name', 'link_type', 'link', 'created_at',)
    list_editable = ('is_active', )
    search_fields = ('name', )
    list_filter = ('link_type', 'is_active')


@admin.register(PublicOffer)
class PublicOfferAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at', 'is_active')
    list_display_links = ('content', 'created_at',)
    list_editable = ('is_active', )
    search_fields = ('content', )
    list_filter = ('is_active',)
    summernote_fields = ('content', )


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_display_links = ('title', 'created_at',)
    list_editable = ('is_active', )
    search_fields = ('title', )
    list_filter = ('is_active', )
    inlines = [AboutImageTabular]

    fieldsets = (
        (None, {'fields': ('title', 'content', 'is_active', 'position')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_content', 'image', 'created_at', 'is_active')
    list_display_links = ('title', 'short_content', 'image', 'created_at',)
    list_editable = ('is_active',)
    search_fields = ('title',)
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('title', 'content', 'image', 'is_active',)}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Requisite)
class RequisiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'created_at', 'is_active')
    list_display_links = ('name', 'value', 'created_at',)
    list_editable = ('is_active',)
    search_fields = ('name',)
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('name', 'value', 'position', 'is_active',)}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)
