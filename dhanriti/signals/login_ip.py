import requests
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from core.settings.base import IP_INFO_KEY
from utils.getIP import get_client_ip


@receiver(user_logged_in)
def get_ip_location(sender, request, user, **kwargs):
    user_ip = get_client_ip(request)
    url = f"https://ipinfo.io/{user_ip}?token={IP_INFO_KEY}"
    response = requests.get(url)
    json = response.json()
    user.last_login_ip = json["ip"]
    user.ip_country = json["country"] if "country" in json else None
    user.save()
