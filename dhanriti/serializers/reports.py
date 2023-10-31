from rest_framework import serializers

from dhanriti.models.reports import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            "external_id",
            "type",
            "reported",
            "report",
            "created_at",
            "judgement",
            "judge_comment",
            "judge_time",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "judgement",
            "judge_comment",
            "judge_time",
        )
