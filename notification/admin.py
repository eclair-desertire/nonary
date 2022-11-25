from django.contrib import admin
from django import forms

from notification.models import Notification


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NotificationAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['product'].queryset = self.fields['product'].queryset.filter(
                main_products__isnull=True
            )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'body', 'image', 'created_at')
    list_display_links = ('title', 'body', 'created_at')
    form = NotificationAdminForm

