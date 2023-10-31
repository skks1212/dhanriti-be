from rest_framework import serializers

from ..models import Comment, CommentLike
from .users import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    commenter = UserSerializer(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    parent_comment = serializers.UUIDField(write_only=True, required=False)
    parent_extID = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "external_id",
            "commenter",
            "likes",
            "liked",
            "comment",
            "replies",
            "parent_comment",
            "parent_extID",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "parent")

    def get_liked(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and not user.is_anonymous:
            return CommentLike.objects.filter(comment=obj, liker=user).exists()
        return False

    def get_likes(self, obj):
        return CommentLike.objects.filter(comment=obj).count()

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent=obj).order_by("created_at")[:10]
        return CommentSerializer(replies, many=True).data

    def get_parent_extID(self, obj):
        if obj.parent:
            return str(obj.parent.external_id)
        return None

    def create(self, validated_data):
        parent_external_id = validated_data.pop("parent_comment", None)

        if parent_external_id:
            try:
                parent_comment = Comment.objects.get(external_id=parent_external_id)
                validated_data["parent"] = parent_comment
            except Comment.DoesNotExist:
                raise serializers.ValidationError("Parent comment not found.")

        return Comment.objects.create(**validated_data)
