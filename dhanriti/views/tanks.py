from django.shortcuts import get_object_or_404
from dhanriti.models.tanks import Canvas, Funnel, Tank
from dhanriti.permissions import IsSelfOrReadOnly
from dhanriti.serializers.tanks import (
    CanvasSerializer,
    FunnelSerializer,
    TankSerializer,
)
from utils.views.base import BaseModelViewSet, BaseModelViewSetPlain
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework import permissions


class CanvasViewSet(
    BaseModelViewSet,
):
    queryset = Canvas.objects.all()
    serializer_class = CanvasSerializer
    permission_classes = (permissions.IsAuthenticated,)

    lookup_field = "external_id"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self):
        external_id = self.kwargs.get(self.lookup_field)

        obj = get_object_or_404(self.get_queryset(), external_id=external_id)
        return obj


class TankViewSet(BaseModelViewSet):
    queryset = Tank.objects.all()
    serializer_class = TankSerializer
    permission_classes = (permissions.IsAuthenticated,)

    lookup_field = "external_id"

    def get_queryset(self):
        return super().get_queryset().filter(canvas__user=self.request.user)

    def get_object(self):
        external_id = self.kwargs.get(self.lookup_field)
        canvas_external_id = self.kwargs.get("canvas_external_id")

        obj = get_object_or_404(
            self.get_queryset(),
            external_id=external_id,
            canvas__external_id=canvas_external_id,
        )
        return obj

    def perform_create(self, serializer):
        canvas_external_id = self.kwargs.get("canvas_external_id")
        canvas = Canvas.objects.get(
            external_id=canvas_external_id, user=self.request.user
        )
        serializer.save(canvas=canvas)

    def destroy(self, request, *args, **kwargs):
        strategy = request.data.get("strategy", "transfer")
        canvas_external_id = self.kwargs.get("canvas_external_id")
        if strategy != "discard":
            canvas = Canvas.objects.get(
            external_id=canvas_external_id, user=self.request.user
            )
            canvas.filled += self.get_object().filled
            canvas.save()

        return super().destroy(request, *args, **kwargs)


class FunnelViewSet(BaseModelViewSet):
    queryset = Funnel.objects.all()
    serializer_class = FunnelSerializer
    permission_classes = (permissions.IsAuthenticated,)

    lookup_field = "external_id"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                canvas__user=self.request.user,
            )
        )

    def get_object(self):
        external_id = self.kwargs.get(self.lookup_field)

        obj = get_object_or_404(
            self.get_queryset(),
            external_id=external_id,
        )
        return obj

    def perform_create(self, serializer):
        in_tank_external_id = self.request.data.get("in_tank_external_id")
        out_tank_external_id = self.request.data.get("out_tank_external_id")

        in_tank = None

        if in_tank_external_id:
            in_tank = Tank.objects.get(
                external_id=in_tank_external_id, canvas__user=self.request.user
            )

        out_tank = Tank.objects.get(external_id=out_tank_external_id, canvas__user=self.request.user)

        print(in_tank, out_tank)

        serializer.save(in_tank=in_tank, out_tank=out_tank, canvas=out_tank.canvas)