import json

import requests
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.settings.base import FCM_APIKEY
from dhanriti.models import Notification, PushNotificationToken
from dhanriti.models.enums import NotificationType


@receiver(
    post_save,
    sender=Notification,
    dispatch_uid="send_push_notification",
)
def send_push_notification(sender, instance: Notification, created, raw, **kwargs):
    if not created or raw:
        # Ignore if it's not a new Notification or if it's a raw signal
        return

    if instance.user.notification_settings.get("allow_push_notifs") is False:
        # The user doesn't want to receive push notifications
        return

    # Get the user's tokens
    tokens = PushNotificationToken.objects.filter(user=instance.user)
    if not tokens.exists():
        # The user doesn't have any tokens
        return

    notification_data = {}
    # Send the notification
    if instance.type == NotificationType.FOLLOW:
        notification_data = {
            "title": f"{instance.content['user']['username']} started following you",
            "tag": "follow",
        }

    if instance.type == NotificationType.CLAP and "part" in instance.content:
        notification_data = {
            "title": f"{instance.content['user']['username']} clapped for your story",
            "body": f"{instance.content['part']['title']}",
            "tag": "clap",
        }

    if instance.type == NotificationType.CLAP and "leaf" in instance.content:
        notification_data = {
            "title": f"{instance.content['user']['username']} clapped for your leaf",
            "tag": "clap",
        }

    if instance.type == NotificationType.COMMENT and "part" in instance.content:
        notification_data = {
            "title": f"{instance.content['user']['username']} commented on {instance.content['part']['title']}",
            "body": f"{instance.content['comment']['comment'][:20]}...",
            "tag": "comment",
        }

    if instance.type == NotificationType.COMMENT and "leaf" in instance.content:
        notification_data = {
            "title": f"{instance.content['user']['username']} commented on your leaf",
            "body": f"{instance.content['comment']['comment'][:20]}...",
            "tag": "comment",
        }

    if instance.type == NotificationType.COMMENT_REPLY:
        notification_data = {
            "title": f"{instance.content['user']['username']} replied to your comment",
            "body": f"{instance.content['comment']['comment'][:20]}...",
            "tag": "comment",
        }

    if instance.type == NotificationType.COMMENT_LIKE:
        notification_data = {
            "title": f"{instance.content['user']['username']} liked your comment",
            "body": f"{instance.content['comment']['comment'][:20]}...",
            "tag": "comment",
        }

    if instance.type == NotificationType.PART_PUBLISH:
        notification_data = {
            "title": f"{instance.content['user']['username']} published a new part",
            "body": f"{instance.content['part']['title']}",
            "tag": "part_publish",
        }

    if instance.type == NotificationType.STORY_VIEWS_MILESTONE:
        notification_data = {
            "title": f" Congratulations! {instance.content['story']['title']} crossed {instance.content['reads']} views",
            "tag": "milestone",
        }

    if instance.type == NotificationType.LEAF_VIEWS_MILESTONE:
        notification_data = {
            "title": f" Congratulations! Your leaf crossed {instance.content['reads']} views",
            "tag": "milestone",
        }

    if instance.type == NotificationType.CLAP_MILESTONE and "story" in instance.content:
        notification_data = {
            "title": f" Congratulations! {instance.content['story']['title']} received {instance.content['claps']} claps",
            "tag": "milestone",
        }

    if instance.type == NotificationType.CLAP_MILESTONE and "leaf" in instance.content:
        notification_data = {
            "title": f" Congratulations! Your leaf received {instance.content['claps']} claps",
            "tag": "milestone",
        }

    if instance.type == NotificationType.REPORT_JUDGEMENT:
        notification_data = {
            "title": f"Your report was {instance.content['report']['judgement']}",
            "tag": "report",
        }

    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": "key=" + FCM_APIKEY,
        "Content-Type": "application/json",
    }

    payload = {
        "registration_ids": [token.token for token in tokens],
        "priority": "high",
        "notification": {
            "title": notification_data["title"],  # Notification title
            "group": notification_data["tag"],  # Notification group
        },
    }
    if "body" in notification_data:
        payload["notification"]["body"] = notification_data["body"]

    result = requests.post(url, data=json.dumps(payload), headers=headers)
    print(result.json())
