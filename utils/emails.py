from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from dhanriti.models.misc import EmailPreset


def generate_email_content(template_id, replacements):
    try:
        template = EmailPreset.objects.get(external_id=template_id).content
        for key, value in replacements.items():
            template = template.replace(f"[{{{key}}}]", value)
        return template
    except EmailPreset.DoesNotExist:
        return None


def send_email(subject, body, to, from_email=None):
    connection = get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    )
    connection.open()
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
        print(from_email)
    email = EmailMessage(subject, body, from_email, to)
    email.content_subtype = "html"
    status = email.send()
    status = True if status == 1 else False
    return status


def send_mass_email(emails):
    connection = get_connection(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    )
    connection.open()
    email_messages = []
    for email in emails:
        print(email)
        email_messages.append(
            EmailMessage(
                email["subject"], email["content"], email["from_email"], email["to"]
            )
        )
    status = connection.send_messages(email_messages)
    connection.close()
    return not status == 0
