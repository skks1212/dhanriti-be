from rest_framework import serializers

from dhanriti.models.notifications import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "external_id",
            "type",
            "read",
            "opened",
            "content",
            "created_at",
        )
