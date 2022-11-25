from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework import permissions

from chat.views import open_chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('api/users/', include('auth_user.urls')),
    path('api/locations/', include('location.urls')),
    path('api/main-page/', include('main_page.urls')),
    path('api/shop/', include('shop.urls')),
    path('api/promo/', include('promo.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/contacts/', include('contact.urls')),
    path('api/filters/', include('app_filter.urls')),
    path('api/order/', include('order.urls')),
    path('api/external/', include('external.urls')),
    path('api/fcm-devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('open-chat/', open_chat, name='open_chat'),
]

if settings.DEBUG:
    # try:
    #     import debug_toolbar
    #     urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    # except ImportError:
    #     pass

    schema_view = get_schema_view(
        openapi.Info(
            title="Small API",
            default_version='v2',
            description="",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="hello@elefanto.kz"),
            license=openapi.License(name="Johny License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    urlpatterns += [path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger')]
