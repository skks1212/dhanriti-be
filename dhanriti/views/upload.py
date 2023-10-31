import math

import requests
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.settings.base import CDN_KEY
from utils.views.mixins import GetPermissionClassesMixin, GetSerializerClassMixin
from dhanriti.models.misc import Asset

from ..models import Part, Story, UploadType
from ..serializers import UploadSerializer


class UploadViewSet(
    GetPermissionClassesMixin,
    GetSerializerClassMixin,
    GenericViewSet,
):
    basename = "upload"
    serializer_class = UploadSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, *args, **kwargs):
        crop_x = int(self.request.query_params.get("x"))
        crop_y = int(self.request.query_params.get("y"))
        crop_w = int(self.request.query_params.get("w"))
        crop_h = int(self.request.query_params.get("h"))
        upload_type = int(self.request.query_params.get("type"))

        if not self.request.user.is_authenticated:
            raise ValidationError({"detail": "You must be logged in to upload a file"})

        # if crop_x is None or crop_y is None or not crop_w or not crop_h:
        #    raise ValidationError({"detail": "Missing crop parameters"})

        if not type:
            raise ValidationError({"detail": "Missing upload type"})

        meta = {
            "type": upload_type,
        }

        sizes = []
        allow = []

        if upload_type == UploadType.PROFILE_PICTURE.value:
            meta["user"] = str(self.request.user.external_id)
            sizes = [100, 200, 400, 800]
            allow = ["png", "jpg"]
            aspect_ratio = 1
            if self.request.user.premium:
                allow.append("gif")

        elif upload_type == UploadType.BACKDROP:
            meta["user"] = str(self.request.user.external_id)
            sizes = [300, 500, 1000, 1200, 1920]
            allow = ["png", "jpg"]
            aspect_ratio = 16 / 7
            if self.request.user.premium:
                allow.append("gif")

        elif upload_type == UploadType.STORY_COVER:
            meta["story"] = self.request.query_params.get("story")
            # if not Story.objects.filter(
            #    external_id=meta["story"], author=self.request.user
            # ).exists():
            #    raise ValidationError({"detail": "Invalid story"})
            sizes = [150, 300, 600, 900]
            allow = ["png", "jpg"]
            aspect_ratio = 2 / 3

        elif upload_type == UploadType.STORY_CONTENT:
            meta["part"] = self.request.query_params.get("part")
            if not Part.objects.filter(
                external_id=meta["part"], story__author=self.request.user
            ).exists():
                raise ValidationError({"detail": "Invalid part"})
            sizes = [500, 1000, 1920]
            allow = ["png", "jpg"]
            aspect_ratio = None
            if self.request.user.premium:
                allow.append("gif")

        elif upload_type == UploadType.LEAF_BACKGROUND:
            meta["user"] = str(self.request.user.external_id)
            sizes = [200, 400, 800, 1600, 2000]
            allow = ["png", "jpg"]
            aspect_ratio = 1
            if self.request.user.premium:
                allow.append("gif")

        elif upload_type == UploadType.LEAF:
            meta["user"] = str(self.request.user.external_id)
            sizes = [200, 400, 800, 1600, 2000]
            allow = ["png", "jpg"]
            aspect_ratio = 1
            if self.request.user.premium:
                allow.append("gif")

        elif upload_type == UploadType.BADGE_ICON:
            meta["badge"] = str(self.request.badge.external_id)
            allow = ["svg"]

        elif upload_type == UploadType.AWARD_ICON:
            meta["award"] = str(self.request.award.external_id)
            allow = ["svg"]

        elif upload_type == UploadType.ASSET:
            meta["asset"] = self.request.query_params.get("asset")
            try:
                asset = Asset.objects.get(external_id=meta["asset"])
            except Asset.DoesNotExist:
                raise ValidationError({"detail": "Invalid asset"})
            sizes = asset.meta.get("sizes", None)
            allow = None
            aspect_ratio = None

        else:
            raise ValidationError({"detail": "Invalid upload type"})

        crop_aspect_ratio = None

        if aspect_ratio:
            rounded_aspect_ratio = math.ceil(aspect_ratio * 100) / 100
        if crop_h and crop_w:
            crop_aspect_ratio = math.ceil((crop_w / crop_h) * 100) / 100

        if (
            aspect_ratio
            and crop_aspect_ratio
            and rounded_aspect_ratio != crop_aspect_ratio
        ):
            raise ValidationError(
                {
                    "detail": "Invalid aspect ratio",
                    "expected": rounded_aspect_ratio,
                    "recieved": crop_aspect_ratio,
                }
            )

        host_url = self.request.scheme + "://" + self.request.get_host()

        req_body = {
            "meta": meta,
            "sizes": sizes,
            "allow": allow,
            "crop": {
                "x": crop_x,
                "y": crop_y,
                "width": crop_w,
                "height": crop_h,
            }
            if crop_aspect_ratio
            else None,
            "callback": host_url + "/v4/upload/callback",
        }

        req_headers = {
            "Authorization": f"Bearer {CDN_KEY}",
        }
        print("----- REQUEST BODY -----")
        print(req_body)
        print("----- REQUEST HEADERS -----")
        print(req_headers)
        try:
            req = requests.post(
                "https://cdn.dhanriti.net/token",
                json=req_body,
                headers=req_headers,
            ).json()

            print("----- REQUEST RESPONSE -----")
            print(req)
        except Exception as e:
            raise ValidationError({"detail": "Failed to upload file"}) from e

        return Response(status=status.HTTP_200_OK, data=req)
