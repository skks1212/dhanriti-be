import requests
from rest_framework import serializers

from core.settings.base import CDN_KEY


def validate_image(url, type, validations):
    req_headers = {
        "Authorization": f"Bearer {CDN_KEY}",
    }

    if url and not url.startswith("https://cdn.dhanriti.net/media/"):
        raise serializers.ValidationError({"cover": "Invalid cover url"})

    img_name = str(url.split("media/")[-1].split(".")[0].split("_")[0])

    try:
        img_url_response = requests.get(
            f"https://cdn.dhanriti.net/info?f={img_name}",
            timeout=5,
            headers=req_headers,
        )
        img_url_json = img_url_response.json()
    except Exception as e:
        raise serializers.ValidationError({"cover": "Unable to verify URL : " + str(e)})

    validation_keys = validations.keys()

    if img_url_response.status_code != 200:
        raise serializers.ValidationError({"cover": "Invalid url"})

    meta = img_url_json.get("meta")

    if meta.get("type") != type:
        raise serializers.ValidationError({"cover": "Invalid url"})

    for key in validation_keys:
        source = img_url_json.get("meta").get(key)
        if not source:
            raise serializers.ValidationError({"cover": "Invalid url"})
        value = validations[key]
        if source != value:
            raise serializers.ValidationError({"cover": "Invalid url"})
