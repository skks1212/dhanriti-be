from rest_framework import serializers

from dhanriti.models.notes import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = (
            "external_id",
            "story",
            "part",
            "title",
            "description",
            "line",
            "color",
            "created_at",
        )
        read_only_fields = ("external_id", "created_at")
