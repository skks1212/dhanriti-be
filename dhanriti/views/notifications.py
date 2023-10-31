from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from utils.views.base import BaseModelViewSetPlain

from ..models import Notification
from ..serializers import NotificationSerializer


class NotificationViewSet(BaseModelViewSetPlain, RetrieveModelMixin, ListModelMixin):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "external_id"
    filterset_fields = ("read", "opened")

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(
        tags=("notifications",), request=None, responses={status.HTTP_200_OK: None}
    )
    @action(detail=True, methods=["post"])
    def read(self, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        tags=("notifications",), request=None, responses={status.HTTP_200_OK: None}
    )
    @action(detail=False, methods=["post"])
    def see(self, *args, **kwargs):
        print(self.get_queryset())
        self.get_queryset().update(opened=True, opened_at=timezone.now())
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        tags=("notifications",), request=None, responses={status.HTTP_200_OK: None}
    )
    @action(detail=False, methods=["post"])
    def read_all(self, *args, **kwargs):
        self.get_queryset().update(read=True)
        return Response(status=status.HTTP_200_OK)
