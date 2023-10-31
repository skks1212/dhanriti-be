from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from utils.emails import generate_email_content
from utils.pagination import CustomLimitOffsetPagination
from utils.views.base import BaseModelViewSet, BaseModelViewSetPlain
from dhanriti.models.enums import VisibilityType
from dhanriti.models.misc import Asset, Email, EmailPreset, Invite, InviteUse
from dhanriti.models.stories import Part, Story
from dhanriti.models.users import User
from dhanriti.serializers.misc import (
    AssetSerializer,
    EmailInviteSerializer,
    EmailPresetSerializer,
    GeneratedStoryPartDataSerializer,
    InviteSerializer,
)

from ..models import Motd, Preset
from ..serializers import MotdSerializer, PresetAdminSerializer, PresetSerializer


class PresetViewSet(
    BaseModelViewSetPlain,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
):
    queryset = Preset.objects.filter(hidden=False)
    serializer_class = PresetSerializer
    permission_classes = (AllowAny,)
    permission_action_classes = {
        "create": (IsAdminUser(),),
        "admin_list": (IsAdminUser(),),
        "admin_retrieve": (IsAdminUser(),),
        "admin_patch": (IsAdminUser(),),
    }
    lookup_field = "external_id"
    filterset_fields = ("type", "priority")

    serializer_action_classes = {
        "admin_list": PresetAdminSerializer,
        "admin_retrieve": PresetAdminSerializer,
        "admin_patch": PresetAdminSerializer,
    }

    @extend_schema(tags=("presets",), description="Get all presets")
    @action(detail=False, methods=["GET"], url_path="admin")
    def admin_list(self, request, *args, **kwargs):
        queryset = Preset.objects.all()
        paginator = CustomLimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, self.request)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    # retrieve for admin
    @extend_schema(tags=("presets",), description="Fetch preset")
    @action(detail=True, methods=["GET"])
    def admin_retrieve(self, request, *args, **kwargs):
        instance = Preset.objects.get(external_id=kwargs["external_id"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(tags=("presets",), description="Edit any presets")
    @action(detail=False, methods=["PATCH"], url_path="(?P<external_id>[^/.]+)/admin")
    def admin_patch(self, request, *args, **kwargs):
        instance = Preset.objects.get(external_id=kwargs["external_id"])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class MotdViewSet(BaseModelViewSetPlain, ListModelMixin):
    queryset = Motd.objects.all()
    serializer_class = MotdSerializer
    permission_classes = (IsAdminUser,)
    permission_action_classes = {"list": (AllowAny(),)}
    lookup_field = "external_id"

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        if not user.is_authenticated:
            queryset = queryset.filter(
                Q(display_for__isnull=True) & Q(expires_on__gt=timezone.now())
            )

        else:
            queryset = queryset.filter(
                (Q(display_for__isnull=True) | Q(display_for=user))
                & Q(expires_on__gt=timezone.now())
            )

        return queryset


class InviteViewSet(
    BaseModelViewSetPlain, RetrieveModelMixin, CreateModelMixin, ListModelMixin
):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    lookup_field = "code"
    permission_classes = (IsAdminUser,)
    permission_action_classes = {
        "retrieve": (AllowAny(),),
        "redeem": (IsAuthenticated(),),
    }

    @action(detail=True, methods=["POST"])
    def redeem(self, request, *args, **kwargs):
        invite: Invite = self.get_object()

        user: User = self.request.user

        if user.closed_beta:
            return Response({"error": "You already have access."}, status=403)

        if invite.uses > invite.max_uses or (
            invite.expires_on and invite.expires_on < timezone.now()
        ):
            return Response({"error": "Invite Expired."}, status=403)

        invite.uses += 1
        InviteUse.objects.create(invite=invite, user=request.user)
        user.closed_beta = True
        user.save()
        invite.save()
        return Response({"message": "Welcome to dhanriti :)"}, status=200)


class EmailPresetViewSet(
    BaseModelViewSet,
):
    queryset = EmailPreset.objects.all()
    serializer_class = EmailPresetSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = "external_id"
    filterset_fields = ("name",)


class AssetViewSet(BaseModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = "external_id"
    filterset_fields = ("name",)


class BetaInviteViewSet(BaseModelViewSetPlain, CreateModelMixin):
    permission_classes = (IsAdminUser,)
    serializer_class = EmailInviteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            usernames = serializer.validated_data["usernames"]
            template_id = serializer.validated_data["template_id"]
            for username in usernames:
                invite = Invite.objects.create(user=User.objects.get(username=username))
                invitelink = f"https://www.dhanriti.net/invite/{invite.code}"
                template = generate_email_content(
                    template_id, {"username": username, "invitelink": invitelink}
                )
                receiver = User.objects.get(username=username).email
                sub = "You have been invited to witness the Future of Literature, before anyone else"

                Email.objects.create(
                    receiver=receiver,
                    sender="noreply@dhanriti.net",
                    template=EmailPreset.objects.get(external_id=template_id),
                    content=template,
                    subject=sub,
                )

            return Response({"message": "Emails sent successfully"}, status=200)


class GeneratedStoryPartViewset(BaseModelViewSetPlain, CreateModelMixin):
    permission_classes = (IsAdminUser,)
    serializer_class = GeneratedStoryPartDataSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bot = User.objects.filter(is_bot=True).order_by("?").first()
        if not bot:
            return Response(
                {"message": "No bot user found. Please create a bot user"},
                status=400,
            )
        if serializer.is_valid():
            validated_data = serializer.validated_data
            story = Story.objects.create(
                title=validated_data["story_title"],
                description=validated_data["story_description"],
                genre=validated_data["genre"],
                cover=validated_data.get("story_cover_url"),
                author=bot,
                visibility=VisibilityType.PUBLIC,
                finished=validated_data.get("story_finished") or True,
                tags=validated_data.get("story_tags"),
            )
            parts_order = []
            # Create parts for the story
            for part in validated_data["part_content"]:
                part = Part.objects.create(
                    story=story,
                    title=part["title"],
                    content=part["content"],
                    visibility=VisibilityType.PUBLIC,
                )
                parts_order.append(part.external_id)
            story.parts_order = parts_order
            story.save()

            return Response({"message": "Story created successfully"}, status=200)

        return Response(serializer.errors, status=400)
