from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from ..models import User


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "full_name",
        )
