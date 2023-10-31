from django.http import Http404
from django_filters.rest_framework import CharFilter, FilterSet, OrderingFilter
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response

from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin

from ..models import Comment, CommentLike, Leaf, Part, Story, VisibilityType
from ..serializers import CommentSerializer


class CommentFilter(FilterSet):
    parent = CharFilter(method="filter_by_parent")
    order_by = OrderingFilter(
        fields=(("created_at", "created_at"), ("likes", "likes")),
        field_labels={"created_at": "Created At", "likes": "likes"},
        label="Order By",
    )

    def filter_by_parent(self, queryset, name, value):
        return Comment.objects.filter(parent__external_id=value)


class CommentViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = "external_id"
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_class = CommentFilter

    def get_queryset(self):
        if "parts" in self.request.path:
            part = Part.objects.get(url=self.kwargs.get("story_part_id"))
            story = Story.objects.get(parts__in=[part])
            if not story.allow_comments or part.visibility < VisibilityType.UNLISTED:
                raise Http404
            queryset = self.queryset.filter(part__url=self.kwargs.get("story_part_id"))
            if self.action == "list":
                queryset = queryset.filter(parent__isnull=True)
            return queryset

        elif "leaves" in self.request.path:
            leaf = Leaf.objects.get(url=self.kwargs.get("leaf_url"))
            if not leaf.allow_comments or leaf.visibility < VisibilityType.UNLISTED:
                raise Http404
            queryset = self.queryset.filter(leaf__url=self.kwargs.get("leaf_url"))
            if self.action == "list":
                queryset = queryset.filter(parent__isnull=True)
            return queryset

    def perform_create(self, serializer):
        if "parts" in self.request.path:
            part = Part.objects.get(url=self.kwargs.get("story_part_id"))
            if part.visibility < VisibilityType.UNLISTED:
                raise Http404
            if part.story.allow_comments:
                serializer.save(
                    commenter=self.request.user,
                    part=part,
                )
            else:
                raise ValidationError("Comments are not allowed on this part.")
        elif "leaves" in self.request.path:
            leaf = Leaf.objects.get(url=self.kwargs.get("leaf_url"))
            if leaf.visibility < VisibilityType.UNLISTED:
                raise Http404
            if leaf.allow_comments:
                serializer.save(
                    commenter=self.request.user,
                    leaf=leaf,
                )
            else:
                raise ValidationError("Comments are not allowed on this leaf.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.commenter == request.user:
            if instance.part:
                instance.part.story.comments -= 1
                instance.part.save()
            elif instance.leaf:
                instance.leaf.comments -= 1
                instance.leaf.save()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        tags=("comments",), request=None, responses={status.HTTP_200_OK: None}
    )
    @action(detail=True, methods=["post"])
    def like(self, request, *args, **kwargs):
        comment = Comment.objects.get(external_id=kwargs.get("external_id"))
        try:
            CommentLike.objects.get(comment=comment, liker=request.user).delete()
            # decrement like count
            comment.likes -= 1
            comment.save()
            return Response({"Status": "Deleted"})
        except CommentLike.DoesNotExist:
            created = CommentLike.objects.create(comment=comment, liker=request.user)
            if created:
                return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_200_OK)
