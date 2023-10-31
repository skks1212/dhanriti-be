from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from utils.verifyURL import validate_image
from dhanriti.models.misc import Invite

from ..models import AssignedBadge, Badge, Follow, Leaf, Notification, Part, Story, User
from ..models.enums import UploadType, VisibilityType
from ..serializers import AssignedBadgeSerializer, BadgeSerializer


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    following_count = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    me_following = serializers.SerializerMethodField(read_only=True)
    story_count = serializers.SerializerMethodField(read_only=True)
    leaf_count = serializers.SerializerMethodField(read_only=True)
    badges = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "about",
            "profile_picture",
            "backdrop",
            "full_name",
            "pronouns",
            "story_count",
            "leaf_count",
            "badges",
            "premium",
            "country",
            "following_count",
            "followers_count",
            "me_following",
            "verified",
        )

    def get_me_following(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return Follow.objects.filter(follower=user, followed=obj).exists()
        return False

    def get_story_count(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return Story.objects.filter(
                author=obj, visibility=VisibilityType.PUBLIC
            ).count()
        return None

    def get_leaf_count(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return Leaf.objects.filter(
                author=obj, visibility=VisibilityType.PUBLIC
            ).count()
        return None

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj).count()

    def get_followers_count(self, obj):
        return Follow.objects.filter(followed=obj).count()

    def get_badges(self, obj):
        # arrange according to badges_order
        badges_order = obj.badges_order
        badges = []
        if badges_order:
            for badge_id in badges_order:
                badge = AssignedBadge.objects.filter(
                    user=obj, badge__external_id=badge_id
                ).first()
                if badge:
                    badges.append(badge)
        return AssignedBadgeSerializer(badges, many=True, context=self.context).data


class UserDetailSerializer(UserSerializer):
    following_count = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    me_following = serializers.SerializerMethodField(read_only=True)
    unopened_notifications = serializers.SerializerMethodField(read_only=True)
    story_count = serializers.SerializerMethodField(read_only=True)
    leaf_count = serializers.SerializerMethodField(read_only=True)
    last_edited_part = serializers.SerializerMethodField(read_only=True)
    badges = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "external_id",
            "username",
            "profile_picture",
            "backdrop",
            "about",
            "full_name",
            "pronouns",
            "premium",
            "country",
            "badges",
            "badges_order",
            "following_count",
            "followers_count",
            "story_count",
            "leaf_count",
            "last_edited_part",
            "notification_settings",
            "story_language",
            "email",
            "verified",
            "me_following",
            "unopened_notifications",
            "account_setup",
            "closed_beta",
        )
        read_only_fields = (
            "external_id",
            "email",
            "premium",
            "username",
            "following_count",
            "followers_count",
            "story_count",
            "leaf_count",
            "verified",
            "account_setup",
            "closed_beta",
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if password := validated_data.pop("password", None):
            instance.set_password(password)
        if "notification_settings" in validated_data:
            notification_settings_data = validated_data.pop(
                "notification_settings", None
            )

            # Check if 'allow_push_notifs' and 'allow_email_notifs' are provided in notification_settings_data
            allow_push_notifs = notification_settings_data.get(
                "allow_push_notifs", None
            )
            allow_email_notifs = notification_settings_data.get(
                "allow_email_notifs", None
            )

            if allow_push_notifs is None:
                allow_push_notifs = instance.notification_settings.get(
                    "allow_push_notifs"
                )
            if allow_email_notifs is None:
                allow_email_notifs = instance.notification_settings.get(
                    "allow_email_notifs"
                )

            notification_settings_data["allow_push_notifs"] = allow_push_notifs
            notification_settings_data["allow_email_notifs"] = allow_email_notifs

            validated_data["notification_settings"] = notification_settings_data

        return super().update(instance, validated_data)

    def validate_profile_picture(self, value):
        profile_picture_url = value
        user_external_id = str(self.context["request"].user.external_id)
        if profile_picture_url:
            validate_image(
                profile_picture_url,
                UploadType.PROFILE_PICTURE,
                {"user": user_external_id},
            )
        return super().validate(value)

    def validate_backdrop(self, value):
        backdrop_url = value
        user_external_id = str(self.context["request"].user.external_id)
        if backdrop_url:
            validate_image(
                backdrop_url, UploadType.BACKDROP, {"user": user_external_id}
            )
        return super().validate(value)

    def get_last_edited_part(self, obj):
        from .stories import LastEditedPartSerializer

        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            part = (
                Part.objects.filter(
                    story__author=obj,
                    visibility__gte=VisibilityType.PRIVATE,
                    last_worked_on__isnull=False,
                )
                .order_by("-last_worked_on")
                .first()
            )

            if part:
                return LastEditedPartSerializer(part, context=self.context).data
        return None

    def get_badges(self, obj):
        # arrange according to badges_order
        badges_order = obj.badges_order
        badges = []
        if badges_order:
            for badge_id in badges_order:
                badge = AssignedBadge.objects.filter(
                    user=obj, badge__external_id=badge_id
                ).first()
                if badge:
                    badges.append(badge)
        return AssignedBadgeSerializer(badges, many=True, context=self.context).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_serializer = UserSerializer(instance, context=self.context)
        data["me_following"] = user_serializer.data.get("me_following")
        data["following_count"] = user_serializer.data.get("following_count")
        data["followers_count"] = user_serializer.data.get("followers_count")
        data["story_count"] = user_serializer.data.get("story_count")
        data["leaf_count"] = user_serializer.data.get("leaf_count")
        return data

    def get_unopened_notifications(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return Notification.objects.filter(user=user, opened=False).count()
        return 0

    def validate_badges_order(self, value):
        if value:
            user = (
                self.context.get("request").user
                if self.context.get("request")
                else None
            )
            if user and not user.is_anonymous:
                assigned_badges = AssignedBadge.objects.filter(user=user)
                assigned_badges_external_ids = [
                    str(badge.badge.external_id) for badge in assigned_badges
                ]

                if len(value) > 3:
                    raise serializers.ValidationError(
                        "Maximum 3 badges allowed to showcase"
                    )
                print(assigned_badges_external_ids)
                for badge in value:
                    print(badge)
                    if str(badge) not in assigned_badges_external_ids:
                        raise serializers.ValidationError("Badge not assigned to user")

        return value


class UserPublicSerializer(UserSerializer):
    following_count = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    me_following = serializers.SerializerMethodField(read_only=True)
    story_count = serializers.SerializerMethodField(read_only=True)
    leaf_count = serializers.SerializerMethodField(read_only=True)
    badges = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "profile_picture",
            "backdrop",
            "about",
            "full_name",
            "pronouns",
            "premium",
            "country",
            "badges",
            "following_count",
            "followers_count",
            "story_count",
            "leaf_count",
            "verified",
            "me_following",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_serializer = UserSerializer(instance, context=self.context)
        data["me_following"] = user_serializer.data.get("me_following")
        data["following_count"] = user_serializer.data.get("following_count")
        data["followers_count"] = user_serializer.data.get("followers_count")
        data["story_count"] = user_serializer.data.get("story_count")
        data["leaf_count"] = user_serializer.data.get("leaf_count")
        data["badges"] = user_serializer.data.get("badges")
        return data


class UserAdminSerializer(UserSerializer):
    invite_sent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "external_id",
            "vishnu_id",
            "account_setup",
            "full_name",
            "username",
            "email",
            "profile_picture",
            "backdrop",
            "about",
            "pronouns",
            "country",
            "notification_settings",
            "badges_order",
            "notes_order",
            "premium",
            "story_language",
            "last_login_platform",
            "last_login_ip",
            "last_online",
            "modified_at",
            "is_bot",
            "closed_beta",
            "invite_sent",
            "preference_points",
        )

    def get_invite_sent(self, obj):
        return Invite.objects.filter(user=obj).exists()
