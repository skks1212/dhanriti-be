from rest_framework import serializers

from utils.verifyURL import validate_image

from ..models import Award, Awarded
from ..models.enums import UploadType


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ("external_id", "icon", "name", "cost", "rarity")

    def validate_icon(self, value):
        icon_url = value
        validate_image(icon_url, UploadType.AWARD_ICON)
        return super().validate(value)


class AwardedSerializer(serializers.ModelSerializer):
    award = AwardSerializer(read_only=True)

    class Meta:
        model = Awarded
        fields = ("external_id", "award", "part", "user", "comment")
