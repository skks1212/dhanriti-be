from rest_framework import serializers

from dhanriti.models import Payment


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "description",
            "amount",
            "external_id",
            "created_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")