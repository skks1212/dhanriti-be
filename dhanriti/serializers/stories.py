from rest_framework import serializers

from utils.getIP import get_client_ip
from utils.verifyHTML import verify_html
from utils.verifyURL import validate_image
from dhanriti.models.stories import StoryRead
from dhanriti.validators import SlugValidator

from ..models import Clap, Part, Story
from ..models.enums import UploadType, VisibilityType


class PartSerializer(serializers.ModelSerializer):
    content_length = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = (
            "external_id",
            "title",
            "published_on",
            "url",
            "content_length",
        )
        read_only_fields = (
            "external_id",
            "title",
            "url",
            "published_on",
            "content_length",
        )

    def get_content_length(self, obj):
        return len(obj.content or "")


class PartWithLastWorkedOnSerializer(PartSerializer):
    last_worked_on = serializers.DateTimeField()

    class Meta:
        model = Part
        fields = PartSerializer.Meta.fields + ("last_worked_on",)


class StorySerializer(serializers.ModelSerializer):
    from .users import UserSerializer

    author = UserSerializer(read_only=True)
    read = serializers.BooleanField(read_only=True, default=False)
    clapped = serializers.SerializerMethodField(read_only=True, default=False)
    content_length = serializers.SerializerMethodField()
    parts_order = serializers.SerializerMethodField()
    last_part_read = serializers.SerializerMethodField()
    parts = serializers.SerializerMethodField()

    parts_order_input = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )

    class Meta:
        model = Story
        fields = (
            "external_id",
            "title",
            "author",
            "description",
            "cover",
            "genre",
            "visibility",
            "language",
            "parts_order",
            "explicit",
            "allow_comments",
            "parts",
            "finished",
            "published_on",
            "reads",
            "last_part_read",
            "claps",
            "comments",
            "tags",
            "read",
            "clapped",
            "url",
            "content_length",
            "parts_order_input",
        )

    def get_content_length(self, obj):
        parts = Part.objects.filter(story=obj)
        return sum([len(part.content or "") for part in parts])

    def get_parts_order(self, obj):
        parts_order = obj.parts_order
        part_urls = Part.objects.filter(
            external_id__in=parts_order, visibility=VisibilityType.PUBLIC
        ).values_list("url", flat=True)
        return part_urls

    def get_last_part_read(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            last_read = (
                StoryRead.objects.filter(reader=user, part__story=obj)
                .order_by("-created_at")
                .first()
            )
            if last_read:
                return last_read.part.url
        elif user and user.is_anonymous:
            print(get_client_ip(self.context.get("request")))

            last_read = (
                StoryRead.objects.filter(
                    reader_ip=get_client_ip(self.context.get("request")),
                    part__story=obj,
                )
                .order_by("-created_at")
                .first()
            )
            if last_read:
                return last_read.part.url
        return None

    def get_clapped(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return Clap.objects.filter(clapper=user, part__in=obj.parts.all()).exists()
        return False

    def update(self, instance, validated_data):
        parts_order_input = validated_data.pop("parts_order_input", None)

        if parts_order_input is not None:
            instance.parts_order = parts_order_input
        return super().update(instance, validated_data)

    def get_parts(self, obj):
        parts_order = obj.parts_order
        parts = Part.objects.filter(
            external_id__in=parts_order, visibility=VisibilityType.PUBLIC
        )
        ordered_parts = sorted(
            parts, key=lambda part: parts_order.index(str(part.external_id))
        )
        serializer = PartSerializer(ordered_parts, many=True)
        return serializer.data


class StoryDetailSerializer(StorySerializer):
    class Meta:
        model = Story
        fields = StorySerializer.Meta.fields + ("allow_comments",)
        read_only_fields = (
            "author",
            "published_on",
            "created_at",
            "last_worked_on",
            "claps",
            "reads",
            "comments",
            "external_id",
        )

    def validate_url(self, value):
        if not self.context["request"].user.premium:
            raise serializers.ValidationError(
                "Only premium users can set custom URLs for their story"
            )
        if self.instance and self.instance.url == value:
            return value
        SlugValidator()(value)
        if Story.objects.filter(url=value).exists():
            raise serializers.ValidationError("Slug already taken")
        return value

    def validate_cover(self, value):
        if value is None:
            return value
        instance = getattr(self, "instance", None)
        cover_url = value
        if cover_url and not instance:
            raise serializers.ValidationError(
                "You can't set a cover image for a story that doesn't exist"
            )
        story_id = instance.external_id
        validate_image(cover_url, UploadType.STORY_COVER, {"story": str(story_id)})
        return cover_url


class StoryEditSerializer(StorySerializer):
    parts = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = StorySerializer.Meta.fields + (
            "parts",
            "allow_comments",
            "last_worked_on",
            "created_at",
            "visibility",
        )

    def get_parts_order(self, obj):
        return obj.parts_order

    def get_parts(self, obj):
        parts_order = obj.parts_order
        parts = Part.objects.filter(
            external_id__in=parts_order, visibility__gte=VisibilityType.PRIVATE
        )
        ordered_parts = sorted(
            parts, key=lambda part: parts_order.index(str(part.external_id))
        )
        part_serializers = StoryPartEditListSerializer(ordered_parts, many=True)
        return part_serializers.data


class StorySerializerAdmin(StoryEditSerializer):
    class Meta:
        model = Story
        fields = StorySerializer.Meta.fields + (
            "allow_comments",
            "last_worked_on",
            "created_at",
            "visibility",
            "preference_points",
        )


class StoryPartSerializer(serializers.ModelSerializer):
    content_length = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = ("external_id", "title", "published_on", "url", "content_length")
        read_only_fields = ("story",)

    def get_content_length(self, obj):
        return len(obj.content or "")


class StoryPartEditListSerializer(StoryPartSerializer):
    is_unpublished = serializers.SerializerMethodField()

    class Meta:
        model = Part
        fields = StoryPartSerializer.Meta.fields + (
            "is_unpublished",
            "last_worked_on",
            "created_at",
            "visibility",
        )
        read_only_fields = StoryPartSerializer.Meta.read_only_fields

    def get_is_unpublished(self, obj):
        return obj.content != obj.unpublished_content


class LastEditedPartSerializer(StoryPartEditListSerializer):
    story_obj = StorySerializer(read_only=True, source="story")

    class Meta:
        model = Part
        fields = StoryPartEditListSerializer.Meta.fields + ("story_obj",)
        read_only_fields = StoryPartEditListSerializer.Meta.read_only_fields


class StoryPartDetailSerializer(StoryPartSerializer):
    story_object = StorySerializer(read_only=True, source="story")

    class Meta:
        model = Part
        fields = StoryPartSerializer.Meta.fields + (
            "story_object",
            "content",
        )
        read_only_fields = StoryPartSerializer.Meta.read_only_fields + (
            "external_id",
            "published_on",
            "last_worked_on",
        )
        

class StoryPartEditSerializer(StoryPartDetailSerializer):
    class Meta:
        model = Part
        fields = StoryPartDetailSerializer.Meta.fields + (
            "unpublished_content",
            "last_worked_on",
            "created_at",
            "visibility",
        )
        read_only_fields = StoryPartDetailSerializer.Meta.read_only_fields

    def validate(self, attrs):
        story_id = self.context["view"].kwargs["story_url"]
        try:
            story = Story.objects.only("id").get(
                url=story_id, author=self.context["request"].user
            )
            attrs["story"] = story
            return super().validate(attrs)
        except Story.DoesNotExist as e:
            raise serializers.ValidationError(
                "You are not the author of this story"
            ) from e

    def validate_url(self, value):
        if not self.context["request"].user.premium:
            raise serializers.ValidationError(
                "Only premium users can set custom URLs for their story"
            )
        if self.instance and self.instance.url == value:
            return value
        SlugValidator()(value)
        if Story.objects.filter(url=value).exists():
            raise serializers.ValidationError("Slug already taken")
        return value

    def validate_content(self, value):
        if self.instance:
            part = self.instance
            if value:
                verify_html(self, value, part.external_id)
        return value

    def validate_unpublished_content(self, value):
        part = self.instance
        if value:
            verify_html(self, value, part.external_id)
        return value
