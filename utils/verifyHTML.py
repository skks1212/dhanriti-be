import requests
from bs4 import BeautifulSoup
from rest_framework import serializers

from core.settings.base import CDN_KEY
from dhanriti.models.enums import UploadType

from .helpers import check_unclosed_tags


def verify_html(self, value, part_id):
    allowed_tags = ["div", "br", "i", "b", "strike", "u", "img"]
    allowed_attributes = {
        "*": ["style"],
        "img": ["src"],
    }

    verified_content = check_unclosed_tags(value)
    if not verified_content:
        raise serializers.ValidationError("Invalid HTML: Some tags are not closed")

    soup = BeautifulSoup(value, "html.parser")
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            raise serializers.ValidationError("Invalid HTML tag")

        # check for attributes
        for attr in tag.attrs:
            if attr == "src":
                continue
            if attr not in allowed_attributes.get("*", []):
                raise serializers.ValidationError("Invalid HTML attribute for tag")

        if tag.name == "img":
            src = tag.get("src")
            file_name = str(src.split("media/")[-1].split(".")[0].split("_")[0])
            req_headers = {
                "Authorization": f"Bearer {CDN_KEY}",
            }
            response = requests.get(
                f"https://cdn.dhanriti.net/info?f={file_name}",
                timeout=5,
                headers=req_headers,
            )
            if response.status_code != 200:
                raise serializers.ValidationError("Invalid image URL")
            else:
                response_json = response.json()
                meta = response_json.get("meta")

                if meta.get("type") != UploadType.STORY_CONTENT or str(
                    meta.get("part")
                ) != str(part_id):
                    raise serializers.ValidationError("Invalid image URL")

    for tag in soup.find_all(attrs={"style": True}):
        style = tag["style"]
        properties = style.split(";")
        for prop in properties:
            if prop.strip() and not prop.strip().startswith("text-align"):
                raise serializers.ValidationError(
                    "Style attribute contains an invalid property"
                )
