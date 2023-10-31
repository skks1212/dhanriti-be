import requests
from rest_framework import serializers

from core.settings.base import CDN_KEY
from dhanriti.validators import SlugValidator

from ..models import Leaf
from ..models.enums import UploadType
from .users import UserSerializer


class LeafSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    clapped = serializers.BooleanField(read_only=True, default=False)
    read = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Leaf
        fields = (
            "external_id",
            "url",
            "author",
            "bg_url",
            "img_url",
            "text",
            "caption",
            "visibility",
            "meta",
            "created_at",
            "comments",
            "reads",
            "claps",
            "clapped",
            "read",
            "allow_comments",
        )
        read_only_fields = (
            "external_id",
            "author",
            "created_at",
            "comments",
            "claps",
            "reads",
            "clapped",
            "allow_comments",
        )

    def validate(self, value):
        if self.partial and not value.get("img_url") and not value.get("bg_url"):
            return super().validate(value)
        req_headers = {
            "Authorization": f"Bearer {CDN_KEY}",
        }
        img_url = value.get("img_url")
        bg_url = value.get("bg_url")
        user_external_id = str(self.context["request"].user.external_id)

        if not user_external_id:
            raise serializers.ValidationError({"author": "Author is required"})

        if not img_url:
            raise serializers.ValidationError({"img_url": "Image URL is required"})

        if not img_url.startswith("https://cdn.dhanriti.net/media/"):
            raise serializers.ValidationError({"img_url": "Invalid image URL"})

        if bg_url and not bg_url.startswith("https://cdn.dhanriti.net/media/"):
            raise serializers.ValidationError({"bg_url": "Invalid image URL"})

        img_name = str(value["img_url"].split("media/")[-1].split(".")[0].split("_")[0])

        try:
            img_url_response = requests.get(
                f"https://cdn.dhanriti.net/info?f={img_name}",
                timeout=5,
                headers=req_headers,
            )
            img_url_json = img_url_response.json()
        except Exception as e:
            raise serializers.ValidationError(
                {"img_url": "Unable to verify URL : " + str(e)}
            )

        if (
            img_url_response.status_code != 200
            or img_url_json.get("meta").get("user") != user_external_id
            or img_url_json.get("meta").get("type") != UploadType.LEAF
        ):
            raise serializers.ValidationError({"img_url": "Invalid image URL (2)"})

        if bg_url:
            bg_name = str(
                value["bg_url"].split("media/")[-1].split(".")[0].split("_")[0]
            )
            try:
                bg_url_response = requests.get(
                    f"https://cdn.dhanriti.net/info?f={bg_name}",
                    timeout=5,
                    headers=req_headers,
                )
            except Exception as e:
                raise serializers.ValidationError(
                    {"bg_url": "Unable to verify URL : " + str(e)}
                )
            bg_url_json = bg_url_response.json()

            if (
                bg_url_response.status_code != 200
                or bg_url_json.get("meta").get("type") != UploadType.LEAF_BACKGROUND
            ):
                raise serializers.ValidationError({"bg_url": "Invalid image URL (2)"})

            if (not bg_url_json.get("meta").get("preset")) and (
                img_url_json.get("meta").get("user") != user_external_id
            ):
                raise serializers.ValidationError({"bg_url": "Invalid image URL (3)"})

        return super().validate(value)

    def validate_url(self, value):
        if not self.context["request"].user.premium:
            raise serializers.ValidationError(
                "Only premium users can set custom URLs for their leaves"
            )
        if self.instance and self.instance.url == value:
            return value
        SlugValidator()(value)
        if Leaf.objects.filter(url=value).exists():
            raise serializers.ValidationError("Slug already taken")
        return value


class LeafAdminSerializer(LeafSerializer):
    class Meta:
        model = Leaf
        fields = LeafSerializer.Meta.fields + ("preference_points",)
