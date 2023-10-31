from celery import shared_task
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string

from utils.emails import send_email, send_mass_email

from ..models import Email, Notification, User


@shared_task
def email_notification(request, cron_key):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    unread_notifications = Notification.objects.filter(read=False)
    users_with_unread_notifications = unread_notifications.values_list(
        "user", flat=True
    ).distinct()
    users = User.objects.filter(
        id__in=users_with_unread_notifications,
        notification_settings__allow_email_notifs=True,
    )
    for user in users:
        receiver = user.email
        user_unread_notifications = unread_notifications.filter(user=user).order_by(
            "-id"
        )
        print(user_unread_notifications)

        email_body = render_to_string(
            "email_template.html",
            {
                "user": user.username,
                "user_unread_notifications": user_unread_notifications[:10],
            },
        )
        sub = str(email_body.split("<li>")[1].split("</a>")[0].split(">")[1])
        sub = sub.replace("\n", "")
        send_email(sub, email_body, [receiver], "dhanriti <info@dhanriti.net>")

    if cron_key is not None:
        return HttpResponse("Executed")


@shared_task
def send_unsent_mails(request=None, cron_key=None):
    if cron_key and cron_key != "3z1OxJQuzkvKKw9ZJDWnZE8R8SuysN7ghdFzwk870UzLXB84ww":
        return HttpResponseForbidden("Incorrect password")

    if cron_key is None:
        pass

    unsent_emails = Email.objects.filter(sent=False)[:100]

    bunch_length = 10
    for i in range(0, len(unsent_emails), bunch_length):
        bunch = unsent_emails[i : i + bunch_length]
        emails_bunch = []
        for email in bunch:
            emails_bunch.append(
                {
                    "subject": email.subject,
                    "content": email.content,
                    "to": [email.receiver],
                    "from_email": "dhanriti <info@dhanriti.net>",
                }
            )

        send_mass_email(emails_bunch)
        Email.objects.filter(id__in=[email.id for email in bunch]).update(sent=True)

    if cron_key is not None:
        return HttpResponse("Executed")
