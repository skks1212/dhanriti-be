from rest_framework import serializers

from ..models import Shelf
from ..models.enums import VisibilityType
from .leaves import LeafSerializer
from .stories import StorySerializer


class ShelfSerializer(serializers.ModelSerializer):
    stories = serializers.SerializerMethodField()
    leaves = LeafSerializer(many=True, read_only=True)

    class Meta:
        model = Shelf
        fields = (
            "name",
            "visibility",
            "created_at",
            "modified_at",
            "description",
            "stories",
            "leaves",
            "cover",
            "external_id",
        )
        read_only_fields = (
            "external_id",
            "created_at",
            "stories",
            "leaves",
            "modified_at",
        )

    def get_stories(self, obj):
        public_stories = obj.stories.filter(visibility=VisibilityType.PUBLIC)
        return StorySerializer(public_stories, many=True).data


class ShelfDetailSerializer(ShelfSerializer):
    class Meta:
        model = Shelf
        fields = ShelfSerializer.Meta.fields
