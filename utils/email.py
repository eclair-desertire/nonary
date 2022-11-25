from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email(email_list, subject, context, template_name):
    from_mail = settings.EMAIL_HOST_USER
    email_tmp = render_to_string(
        template_name,
        context
    )
    msg = EmailMultiAlternatives(subject, email_tmp, from_mail, email_list)
    msg.attach_alternative(email_tmp, "text/html")
    msg.send()
