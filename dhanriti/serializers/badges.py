from rest_framework import serializers

from utils.verifyURL import validate_image

from ..models import AssignedBadge, Badge
from ..models.enums import UploadType


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ("external_id", "icon", "name", "description", "rarity", "created_at")

    def validate_icon(self, value):
        icon_url = value
        validate_image(icon_url, UploadType.BADGE_ICON)
        return super().validate(value)


class AssignedBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = AssignedBadge
        fields = ("badge", "created_at")
