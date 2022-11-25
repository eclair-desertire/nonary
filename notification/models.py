from django.conf import settings
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField

from notification.services.admin.send_message import send_message, send_notification
from utils.choices import StoryTypeChoices
from utils.models import BaseModel


class Notification(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    body = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    image = ProcessedImageField(upload_to='notifications', processors=[], format='WEBP', options={'quality': 60},
                                null=True, blank=True)
    promotion = models.ForeignKey('main_page.Stock', on_delete=models.CASCADE, blank=True, null=True,
                                  verbose_name='Акция')
    # banner = models.ForeignKey('main_page.Story', on_delete=models.CASCADE, blank=True, null=True,
    #                            limit_choices_to={'story_type': StoryTypeChoices.MINI}, verbose_name='Баннер')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, blank=True, null=True,
                                limit_choices_to={'main_products__isnull': True}, verbose_name='Товар')

    def save(self, **kwargs):
        notify = False
        if not self.pk:
            notify = True
        super(Notification, self).save(**kwargs)
        if notify:
            image_url = ''
            if self.image:
                image_url = f"{settings.CURRENT_SITE}/{self.image.url}"
            data = {
                'title': self.title,
                'body': self.body,
                'image': image_url,
            }
            send_notification(data=self.notification_type, notification=data)

    @property
    def notification_type(self):
        if self.promotion:
            return {
                'notification_type': 'promotion',
                'promotion': str(self.promotion_id),
                # 'banner': '',
                'product_slug': '',
                'product_id': '',
            }
        # if self.banner:
        #     return {
        #         'notification_type': 'banner',
        #         'promotion': '',
        #         'banner': str(self.banner_id),
        #         'product_slug': '',
        #     }
        if self.product:
            return {
                'notification_type': 'product',
                'promotion': '',
                # 'banner': '',
                'product_slug': self.product.slug,
                'product_id': str(self.product_id),
            }
        return {
            'notification_type': 'other',
            'promotion': '',
            # 'banner': '',
            'product_slug': '',
            'product_id': '',
        }

    class Meta:
        verbose_name = 'Пуш уведомление'
        verbose_name_plural = 'Пуш уведомления'
        ordering = ('-created_at', )
