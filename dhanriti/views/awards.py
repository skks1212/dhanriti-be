from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny, IsAdminUser

from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin

from ..models import Award, Awarded, Part, Story
from ..serializers import AwardedSerializer, AwardSerializer


class AwardViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    ListModelMixin,
    PartialUpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = (IsAdminUser,)
    permission_action_classes = {"list": (AllowAny(),), "retrieve": (AllowAny(),)}
    lookup_field = "external_id"

    def get_queryset(self):
        return self.queryset.all()

    def perform_create(self, serializer):
        serializer.save()
        return super().perform_create(serializer)


class AwardedViewSet(BaseModelViewSetPlain, RetrieveModelMixin, ListModelMixin):
    queryset = Awarded.objects.all()
    serializer_class = AwardedSerializer
    lookup_field = "external_id"
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = super().get_queryset()
        story_url = self.kwargs.get("story_url")
        part_url = self.kwargs.get("part_url")
        if story_url:
            story = get_object_or_404(Story, url=story_url)
            queryset = queryset.filter(part__story=story)
        elif part_url:
            part = get_object_or_404(Part, url=part_url)
            queryset = queryset.filter(part=part)

        return queryset
