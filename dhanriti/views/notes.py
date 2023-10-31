from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)

from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin

from ..models import Note, Part, Story
from ..serializers import NoteSerializer


class NoteViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "external_id"

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        story = self.request.query_params.get("story")
        part = self.request.query_params.get("part")
        if story is not None:
            queryset = queryset.filter(story=story)

        if part is not None:
            queryset = queryset.filter(part=part)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            story_ext_id = self.request.data.get("story")
            part_ext_id = self.request.data.get("part")
            story = Story.objects.filter(
                external_id=story_ext_id, author=self.request.user
            ).first()
            part = Part.objects.filter(
                external_id=part_ext_id, story__author=self.request.user
            ).first()
            if not story and not part:
                raise PermissionDenied(code=403)

            serializer.save(user=self.request.user, story=story)
        else:
            raise PermissionDenied("You must be authenticated to create a note.")
