from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from dhanriti.models import Login


class AuthSerializer(AuthTokenSerializer):
    email = serializers.EmailField(label=_("Username"), write_only=True)
    username = None

    def validate(self, attrs):
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)


class VishnuLoginSerializer(serializers.Serializer):
    service_token = serializers.CharField(read_only=True, required=False)
    client_url = serializers.CharField(write_only=True, required=False)
    login_token = serializers.CharField(write_only=True, required=False)
    url = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)


class VishnuCheckLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = ("service_token", "successful", "token")
        read_only_fields = ("service_token", "successful", "token")
