import datetime

from rest_framework import serializers

from dhanriti.models.misc import Asset, Invite

from ..models import EmailPreset, Motd, Preset, StoryRead
from .stories import StorySerializer
from .users import UserSerializer


class PresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = ("external_id", "type", "content", "priority", "premium", "name")


class PresetAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = (
            "external_id",
            "type",
            "content",
            "priority",
            "premium",
            "name",
            "hidden",
        )


class MotdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motd
        fields = ("external_id", "icon", "title", "message", "action", "created_at")


class InviteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    code = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Invite
        fields = ("code", "uses", "max_uses", "expires_on", "created_at", "user")
        read_only_fields = ("user",)


class EmailPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPreset
        fields = (
            "external_id",
            "name",
            "description",
            "created_by",
            "content",
            "created_at",
        )


class EmailInviteSerializer(serializers.Serializer):
    usernames = serializers.ListField(child=serializers.CharField())
    template_id = serializers.CharField()


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            "external_id",
            "name",
            "description",
            "created_by",
            "created_at",
            "url",
            "meta",
        )


class GeneratedStoryPartDetailSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()


class GeneratedStoryPartDataSerializer(serializers.Serializer):
    story_title = serializers.CharField()
    story_description = serializers.CharField()
    genre = serializers.IntegerField()
    story_cover_url = serializers.CharField(required=False, allow_null=True)
    story_tags = serializers.ListField(child=serializers.CharField(), required=False)
    story_finished = serializers.BooleanField(required=False)
    part_content = GeneratedStoryPartDetailSerializer(many=True)

    class Meta:
        fields = (
            "story_title",
            "story_description",
            "genre",
            "story_cover_url",
            "part_content",
        )


class StoryStatSerializer(serializers.Serializer):
    story = serializers.SerializerMethodField()
    total_reads = serializers.SerializerMethodField()
    today_reads = serializers.SerializerMethodField()
    yesterday_reads = serializers.SerializerMethodField()
    current_week_reads = serializers.SerializerMethodField()
    last_week_reads = serializers.SerializerMethodField()
    current_month_reads = serializers.SerializerMethodField()
    last_month_reads = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "story",
            "total_reads",
            "today_reads",
            "yesterday_reads",
            "current_week_reads",
            "last_week_reads",
            "current_month_reads",
            "last_month_reads",
        )

    def get_story(self, obj):
        # return all the data from the story serializer
        story = StorySerializer(obj).data
        return story

    def get_total_reads(self, obj):
        return obj.reads

    def get_today_reads(self, obj):
        today_reads = StoryRead.objects.filter(
            part__story=obj, created_at__date=datetime.date.today()
        ).count()
        return today_reads

    def get_yesterday_reads(self, obj):
        yesterday_reads = StoryRead.objects.filter(
            part__story=obj,
            created_at__date=datetime.date.today() - datetime.timedelta(days=1),
        ).count()
        return yesterday_reads

    def get_current_week_reads(self, obj):
        current_week_reads = StoryRead.objects.filter(
            part__story=obj,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=7),
        ).count()
        return current_week_reads

    def get_last_week_reads(self, obj):
        last_week_reads = StoryRead.objects.filter(
            part__story=obj,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=14),
            created_at__lte=datetime.date.today() - datetime.timedelta(days=7),
        ).count()
        return last_week_reads

    def get_current_month_reads(self, obj):
        current_month_reads = StoryRead.objects.filter(
            part__story=obj,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=30),
        ).count()
        return current_month_reads

    def get_last_month_reads(self, obj):
        last_month_reads = StoryRead.objects.filter(
            part__story=obj,
            created_at__gte=datetime.date.today() - datetime.timedelta(days=60),
            created_at__lte=datetime.date.today() - datetime.timedelta(days=30),
        ).count()
        return last_month_reads
