from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from ..models import User
from ..models.pushnotifications import PushNotificationToken
from ..serializers import UserSerializer


class PushNotificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushNotificationToken
        fields = ("token", "device")
