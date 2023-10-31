from rest_framework import serializers

from ..models import Search


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ("external_id", "query", "created_at")
        read_only_fields = ("external_id", "created_at")
