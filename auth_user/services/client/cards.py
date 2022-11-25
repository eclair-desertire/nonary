from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from utils.current_site import get_current_domain_with_protocol


def register_card(request):
    current_site = get_current_domain_with_protocol(request)
    user_id = urlsafe_base64_encode(force_bytes(request.user.id))
    url = f'{settings.CARD_TOKEN_URL}?approveUrl={current_site}/api/users/save-card-success/{user_id}/' \
          f'&declineUrl={current_site}/api/users/save-card-decline/{user_id}/'
    return url
