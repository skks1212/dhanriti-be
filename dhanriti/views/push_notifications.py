from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.views.base import BaseModelViewSetPlain

from ..models.pushnotifications import PushNotificationToken
from ..serializers.pushnotifications import PushNotificationTokenSerializer


class PushNotificationTokenViewSet(
    BaseModelViewSetPlain, CreateModelMixin, DestroyModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = PushNotificationTokenSerializer
    lookup_field = "external_id"
    queryset = PushNotificationToken.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        token = serializer.validated_data.get("token")

        existing_token = self.queryset.filter(token=token)

        if existing_token.count() > 0:
            return Response(
                {"detail": "Token already exists"},
                status=status.HTTP_200_OK,
            )

        serializer.save(user=self.request.user)
        return super().perform_create(serializer)
