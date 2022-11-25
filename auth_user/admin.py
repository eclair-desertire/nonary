from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, AdminPasswordChangeForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django_db_logger.admin import StatusLogAdmin
from fcm_django.models import FCMDevice

from auth_user.models import Question, QuestionCategory, BadSMS, UserCard
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy
from django_db_logger.models import StatusLog


try:
    admin.site.unregister(Group)
except:
    pass


try:
    admin.site.unregister(StatusLog)
except:
    pass


admin.site.unregister(TokenProxy)
# admin.site.unregister(FCMDevice)


User = get_user_model()


class CustomAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'middle_name',
            'city',
            'old_phone_number',
            'verification_code',
            'avatar',
        )}),
        ('Permissions', {'fields': (
            'is_superuser',
            'is_admin',
            'is_active',
            'is_staff',
            'is_common',
        )}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('phone_number', 'password1', 'password2')}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'middle_name',
            'city',
            'avatar',
        )}),
        ('Permissions', {'fields': (
            'is_superuser',
            'is_admin',
            'is_active',
            'is_staff',
            'is_common',
        )}),
    )
    limited_fieldsets = (
        (None, {'fields': ('phone_number',)}),
        ('Personal info', {'fields': (
            'first_name',
            'last_name',
            'middle_name',
            'city',
            'old_phone_number',
            'verification_code',
            'avatar',
        )}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('phone_number', 'email', 'last_name', 'first_name', 'middle_name', 'is_superuser',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('phone_number', 'first_name', 'last_name', 'middle_name')
    readonly_fields = ('date_joined',)
    ordering = ('phone_number', 'email',)


admin.site.register(User, CustomAdmin)


@admin.register(StatusLog)
class StatusLogAdmin(StatusLogAdmin):

    def get_model_perms(self, request):

        return {
            "add": False,
            "change": False,
            "delete": False,
            "view": not request.user.is_common,
        }


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'updated_at', 'is_active')
    list_display_links = ('question', 'answer', 'updated_at', 'is_active')


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'icon')
    list_display_links = ('name', 'created_at', 'icon')


@admin.register(BadSMS)
class BadSMSAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'description')
    list_display_links = ('phone_number', 'code', 'description')


@admin.register(UserCard)
class UserCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_token', 'created_at', 'pan', 'brand')
    list_display_links = ('user', 'card_token', 'created_at', 'pan', 'brand')

    list_filter = ('brand', )
