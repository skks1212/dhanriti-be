from django.db.models import Count, Exists, OuterRef, Q
from django.http import Http404
from django.utils import timezone
from django.utils.timezone import now, timedelta
from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
    OrderingFilter,
)
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response

from utils.helpers import get_client_ip
from utils.pagination import CustomLimitOffsetPagination
from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin
from dhanriti.serializers.stories import StoryEditSerializer, StoryPartEditSerializer

from ..models import Clap, Part, Shelf, ShelfStory, Story, StoryRead
from ..models.enums import GenreType, VisibilityType
from ..permissions import IsAuthor, IsAuthorOrReadOnly, IsStoryAuthorOrReadOnly
from ..serializers import (
    StoryDetailSerializer,
    StoryPartDetailSerializer,
    StorySerializer,
    StorySerializerAdmin,
    StoryStatSerializer,
)


class StoryFilter(FilterSet):
    author = CharFilter(field_name="author__username", lookup_expr="exact")
    visibility = NumberFilter(field_name="visibility", lookup_expr="exact")
    genre = NumberFilter(field_name="genre", lookup_expr="exact")
    title = CharFilter(field_name="title", lookup_expr="icontains")
    shelf_id = CharFilter(method="filter_by_shelf_id")
    short_read = BooleanFilter(method="filter_short_read", label="Short Read")
    recommended = BooleanFilter(method="filter_recommended", label="Recommended")
    allow_explicit = BooleanFilter(method="filter_explicit", lookup_expr="exact")

    order_by = OrderingFilter(
        fields=(("reads", "trending"), ("created_at", "created_at")),
        field_labels={"reads": "Trending", "created_at": "Created At"},
        label="Order By",
    )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        order_by_value = self.form.cleaned_data.get("order_by")
        if order_by_value:
            if "trending" in order_by_value:
                twenty_four_hours_ago = now() - timedelta(hours=24)
                queryset = (
                    queryset.filter(
                        visibility__gte=VisibilityType.PUBLIC,
                        parts__storyread__created_at__gte=twenty_four_hours_ago,
                        parts__storyread__deleted=False,
                    )
                    .order_by("-reads")
                    .distinct()
                )
            elif "-trending" in order_by_value:
                twenty_four_hours_ago = now() - timedelta(hours=24)
                queryset = (
                    queryset.filter(
                        visibility__gte=VisibilityType.PUBLIC,
                        parts__storyread__created_at__gte=twenty_four_hours_ago,
                        parts__storyread__deleted=False,
                    )
                    .order_by("reads")
                    .distinct()
                )
            elif "created_at" in order_by_value:
                queryset = queryset.order_by("-created_at")
            elif "-created_at" in order_by_value:
                queryset = queryset.order_by("created_at")

        return queryset

    def filter_by_shelf_id(self, queryset, name, value):
        try:
            shelf = Shelf.objects.get(
                external_id=value, visibility__gte=VisibilityType.UNLISTED
            )
            stories = list(
                ShelfStory.objects.filter(shelf=shelf).values_list(
                    "story__id", flat=True
                )
            )
            return queryset.filter(id__in=stories)
        except Shelf.DoesNotExist:
            return queryset.none()

    def filter_short_read(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(
                public_part_count=Count(
                    "parts", filter=Q(parts__visibility__gte=VisibilityType.PUBLIC)
                )
            )
            queryset = queryset.filter(public_part_count=1)
        return queryset

    def filter_recommended(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            last_read_story_by_user = (
                StoryRead.objects.filter(reader=self.request.user)
                .order_by("-created_at")
                .first()
            )
            if last_read_story_by_user:
                queryset = queryset.filter(
                    genre=last_read_story_by_user.part.story.genre
                )
                # exclude stories that the user has already read
                queryset = queryset.exclude(
                    parts__storyread__reader=self.request.user,
                    parts__storyread__deleted=False,
                )

        return queryset

    def filter_explicit(self, queryset, name, value):
        if value:
            return queryset


class StoryViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Story.objects.all()
    lookup_field = "url"
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_action_classes = {
        "list": StorySerializer,
        "edit": StoryEditSerializer,
        "list_edit": StoryEditSerializer,
        "admin": StorySerializerAdmin,
        "admin_update": StorySerializerAdmin,
        "stats": StoryStatSerializer,
        "stats_all": StoryStatSerializer,
    }

    permission_action_classes = {
        "list": (permissions.AllowAny(),),
        "trending": (permissions.AllowAny(),),
        "retrieve": (permissions.AllowAny(),),
        "my_stories": (permissions.IsAuthenticated(),),
        "genres": (permissions.AllowAny(),),
        "shelf": (permissions.AllowAny(),),
        "admin": (permissions.IsAdminUser(),),
        "stats": (IsAuthor(),),
        "stats_all": (IsAuthor(),),
    }
    filterset_class = StoryFilter

    def get_serializer_class(self):
        if self.action in self.serializer_action_classes:
            return self.serializer_action_classes[self.action]
        return StoryDetailSerializer

    def get_object(self):
        return super().get_object()

    def get_queryset(self):
        queryset = super().get_queryset()
        user_filter = self.request.query_params.get("author")
        if self.action in ("list", "trending", "recommended"):
            queryset = queryset.filter(
                visibility__gte=VisibilityType.PUBLIC,
                parts__visibility__gte=VisibilityType.PUBLIC,
            )

            if not user_filter:
                queryset = queryset.filter(preference_points__gte=0)

            queryset = queryset.distinct().order_by("-preference_points")

        elif self.action in ["list_edit", "edit", "partial_update", "destroy"]:
            queryset = queryset.filter(author=self.request.user, explicit=False)
            queryset = queryset.prefetch_related("parts")
        elif self.action in ["admin", "stats", "stats_all"]:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(visibility__gte=VisibilityType.UNLISTED)

        explicit_filter = self.request.query_params.get("allow_explicit")
        if not explicit_filter and explicit_filter != "true":
            queryset = queryset.filter(explicit=False)

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                read=Exists(
                    StoryRead.objects.filter(
                        part__story_id=OuterRef("id"),
                        reader_id=self.request.user.id,
                    )
                ),
                clapped=Exists(
                    Clap.objects.filter(
                        part__story_id=OuterRef("id"),
                        clapper_id=self.request.user.id,
                    )
                ),
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        tags=("stories",), description="List stories based on recommendations"
    )
    @action(methods=["GET"], detail=False)
    def recommended(self, *args, **kwargs):
        return self.list(*args, **kwargs)

    @extend_schema(tags=("stories",), description="List top stories in each genre")
    @action(detail=False, methods=["get"])
    def genres(self, *args, **kwargs):
        genres = []
        for g in GenreType:
            story = (
                self.get_queryset()
                .filter(genre=g.value, cover__startswith="https://cdn.dhanriti")
                .first()
            )

            if story:
                genres.append({"genre": g.value, "story": StorySerializer(story).data})

        return Response(genres)

    @extend_schema(tags=("stories",), description="List user's stories")
    @action(detail=False, methods=["get"], url_path="edit")
    def list_edit(self, *args, **kwargs):
        return self.list(*args, **kwargs)

    @extend_schema(tags=("stories",), description="Retrieve user's stories")
    @action(detail=False, methods=["get"], url_path="(?P<url>[^/.]+)/edit")
    def edit(self, *args, **kwargs):
        return self.retrieve(*args, **kwargs)

    @extend_schema(tags=("stories",), description="List all stories")
    @action(detail=False, methods=["get"])
    def admin(self, *args, **kwargs):
        return self.list(*args, **kwargs)

    # PATCH /stories/<story_id>/admin
    @extend_schema(tags=("stories",), description="Update a story")
    @action(detail=False, methods=["patch"], url_path="(?P<external_id>[^/.]+)/admin")
    def admin_update(self, *args, **kwargs):
        external_id = kwargs.get("external_id")
        story = Story.objects.get(external_id=external_id)
        serializer = StorySerializerAdmin(story, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(tags=("stories",), description="Stats for a story")
    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # stat for all stories
    @extend_schema(tags=("stories",), description="Stats for all stories")
    @action(detail=False, methods=["get"], url_path="stats")
    def stats_all(self, *args, **kwargs):
        queryset = self.get_queryset().filter(author=self.request.user)
        paginator = CustomLimitOffsetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, self.request)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class StoryPartViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Part.objects.all()
    serializer_class = StoryPartDetailSerializer
    lookup_url_kwarg = "id"
    permission_classes = (IsStoryAuthorOrReadOnly,)
    serializer_action_classes = {
        "create": StoryPartEditSerializer,
        "partial_update": StoryPartEditSerializer,
        "edit": StoryPartEditSerializer,
    }
    permission_action_classes = {
        "list": (permissions.AllowAny(),),
        "retrieve": (permissions.AllowAny(),),
    }

    def get_queryset(self):
        queryset = super().get_queryset().filter(visibility__gte=VisibilityType.PUBLIC)
        if story_id := self.kwargs.get("story_url"):
            queryset = queryset.filter(story__url=story_id)

        if self.action != "list" and self.request.user.is_authenticated:
            queryset |= (
                super()
                .get_queryset()
                .filter(
                    story__author=self.request.user, visibility=VisibilityType.PRIVATE
                )
            )

        if self.action == "edit":
            queryset = Part.objects.filter(story__author=self.request.user)
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        id = self.kwargs[self.lookup_url_kwarg]

        obj = get_object_or_404(queryset, url=id)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        read_kwargs = {"part": instance}
        if request.user.is_authenticated:
            read_kwargs["reader"] = request.user
        else:
            read_kwargs["reader_ip"] = get_client_ip(request)
        read: StoryRead = (
            StoryRead.objects.filter(**read_kwargs).order_by("-created_at").first()
        )
        if not read or read.created_at < now() - timedelta(minutes=5):
            StoryRead.objects.create(**read_kwargs)

        return Response(self.get_serializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = Part.objects.get(
            story__url=kwargs["story_url"], url=kwargs["id"], story__author=request.user
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        instance = Part.objects.get(
            story__url=kwargs["story_url"], url=kwargs["id"], story__author=request.user
        )
        partial = kwargs.pop("partial", True)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Update the last_worked_on field to the current time
        serializer.validated_data["last_worked_on"] = timezone.now()

        serializer.save()
        return Response(serializer.data)

    @extend_schema(tags=("parts",))
    @action(detail=True, methods=["get"])
    def edit(self, *args, **kwargs):
        part = self.get_object()
        return Response(StoryPartEditSerializer(part).data)

    @extend_schema(
        tags=("parts",), request=None, responses={status.HTTP_201_CREATED: None}
    )
    @action(detail=True, methods=["post"])
    def clap(self, request, *args, **kwargs):
        instance = self.queryset.get(story__url=kwargs["story_url"], url=kwargs["id"])
        if instance.visibility < VisibilityType.UNLISTED:
            raise Http404
        if Clap.objects.filter(part=instance, clapper=request.user).exists():
            clap = Clap.objects.filter(part=instance, clapper=request.user)
            clap.delete()
            return Response({"Status": "Deleted"})
        else:
            created = Clap.objects.get_or_create(part=instance, clapper=request.user)
            if created:
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_200_OK)
