from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin

from ..models import AssignedBadge, Badge, User
from ..serializers import AssignedBadgeSerializer, BadgeSerializer


class BadgeViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    PartialUpdateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = (IsAdminUser,)
    permission_action_classes = {"list": (AllowAny(),), "retrieve": (AllowAny(),)}
    lookup_field = "external_id"

    def get_queryset(self):
        return self.queryset.all()

    def perform_create(self, serializer):
        serializer.save()
        return super().perform_create(serializer)


class AssignedBadgeViewSet(BaseModelViewSetPlain, RetrieveModelMixin, ListModelMixin):
    queryset = AssignedBadge.objects.all()
    serializer_class = AssignedBadgeSerializer
    lookup_field = "external_id"
    permission_classes = [
        AllowAny,
    ]

    @action(detail=False, methods=["get"], url_path="(?P<username>[^/.]+)/badges")
    def user_badges(self, request, *args, **kwargs):
        username = kwargs.get("username")
        user = get_object_or_404(User, username=username)
        assigned_badges = self.queryset.filter(user=user)
        serializer = self.get_serializer(assigned_badges, many=True)
        return Response(serializer.data)
