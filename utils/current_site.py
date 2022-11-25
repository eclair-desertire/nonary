from django.contrib.sites.shortcuts import get_current_site


def get_current_domain_with_protocol(request):
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    return f'{protocol}://{current_site}'
