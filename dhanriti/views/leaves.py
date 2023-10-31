from django.db.models import Exists, OuterRef
from django.http import Http404
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
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response

from utils.helpers import get_client_ip
from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin

from ..models import Clap, Follow, Leaf, LeafRead, Shelf, ShelfLeaf
from ..models.enums import VisibilityType
from ..permissions import IsAuthorOrReadOnly
from ..serializers import LeafAdminSerializer, LeafSerializer


class LeafFilter(FilterSet):
    author = CharFilter(field_name="author__username", lookup_expr="exact")
    visibility = NumberFilter(field_name="visibility", lookup_expr="exact")
    text = CharFilter(field_name="text", lookup_expr="icontains")
    caption = CharFilter(field_name="caption", lookup_expr="icontains")
    shelf_id = CharFilter(method="filter_by_shelf_id")
    following = BooleanFilter(method="filter_by_following")
    unread = BooleanFilter(method="filter_by_unread")

    order_by = OrderingFilter(
        fields=(("reads", "trending"),),
        field_labels={"reads": "Trending"},
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
                        leafread__created_at__gte=twenty_four_hours_ago,
                    )
                    .order_by("-reads")
                    .distinct()
                )
            elif "-trending" in order_by_value:
                twenty_four_hours_ago = now() - timedelta(hours=24)
                queryset = (
                    queryset.filter(
                        visibility__gte=VisibilityType.PUBLIC,
                        leafread__created_at__gte=twenty_four_hours_ago,
                    )
                    .order_by("reads")
                    .distinct()
                )

        return queryset

    def filter_by_shelf_id(self, queryset, name, value):
        try:
            shelf = Shelf.objects.get(
                external_id=value, visibility__gte=VisibilityType.UNLISTED
            )
            leaves = list(
                ShelfLeaf.objects.filter(shelf=shelf).values_list("leaf__id", flat=True)
            )
            return queryset.filter(id__in=leaves)
        except Shelf.DoesNotExist:
            return queryset.none()

    def filter_by_following(self, queryset, name, value):
        if value:
            user = self.request.user
            if not user.is_authenticated:
                return queryset.none()
            following = Follow.objects.filter(follower=user).values_list(
                "followed", flat=True
            )
            return queryset.filter(author__in=following).order_by("-claps")

        return queryset

    def filter_by_unread(self, queryset, name, value):
        if value:
            user = self.request.user
            if not user.is_authenticated:
                return queryset.none()
            read = LeafRead.objects.filter(reader=user).values_list(
                "leaf__id", flat=True
            )
            return queryset.exclude(id__in=read).order_by("-claps")

        return queryset


class LeafViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Leaf.objects.all()
    lookup_field = "url"
    permission_classes = (IsAuthorOrReadOnly,)
    permission_action_classes = {
        "list": (permissions.AllowAny(),),
        "retrieve": (permissions.AllowAny(),),
        "my_leaves": (permissions.IsAuthenticated(),),
        "admin": (permissions.IsAdminUser(),),
    }
    filterset_class = LeafFilter
    serializer_class = LeafSerializer
    serializer_action_classes = {
        "admin": LeafAdminSerializer,
    }

    def get_object(self):
        return super().get_object()

    def get_queryset(self):
        queryset = super().get_queryset()

        user_filter = self.request.query_params.get("author")
        if self.action in ["list", "recommended", "trending"]:
            queryset = queryset.filter(visibility__gte=VisibilityType.PUBLIC)
            if not user_filter:
                queryset = queryset.filter(preference_points__gte=0)
            queryset = queryset.distinct().order_by("-preference_points")
        elif self.action == "my_leaves":
            queryset = queryset.filter(author=self.request.user)
        else:
            queryset = queryset.filter(visibility__gte=VisibilityType.UNLISTED)

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                clapped=Exists(
                    Clap.objects.filter(
                        leaf__id=OuterRef("id"), clapper_id=self.request.user.id
                    )
                ),
                read=Exists(
                    LeafRead.objects.filter(
                        leaf__id=OuterRef("id"), reader_id=self.request.user.id
                    )
                ),
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        read_kwargs = {"leaf": instance}
        if request.user.is_authenticated:
            read_kwargs["reader"] = request.user
        else:
            read_kwargs["reader_ip"] = get_client_ip(request)
        read: LeafRead = (
            LeafRead.objects.filter(**read_kwargs).order_by("-created_at").first()
        )
        if not read or read.created_at < now() - timedelta(minutes=5):
            LeafRead.objects.create(**read_kwargs)

        return Response(self.get_serializer(instance).data)

    @extend_schema(
        tags=("leaves",), request=None, responses={status.HTTP_201_CREATED: None}
    )
    @action(detail=True, methods=["post"])
    def clap(self, request, *args, **kwargs):
        instance = self.queryset.get(url=kwargs.get("url"))
        if instance.visibility < VisibilityType.UNLISTED:
            raise Http404
        if Clap.objects.filter(clapper=request.user, leaf=instance).exists():
            clap = Clap.objects.filter(clapper=request.user, leaf=instance)
            clap.delete()
            return Response({"Status": "Deleted"})
        else:
            created = Clap.objects.get_or_create(clapper=request.user, leaf=instance)
            if created:
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_200_OK)

    @extend_schema(
        tags=("leaves",), request=None, responses={status.HTTP_201_CREATED: None}
    )
    @action(detail=False, methods=["get"])
    def my_leaves(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(tags=("leaves",), description="List all leaves")
    @action(detail=False, methods=["get"])
    def admin(self, *args, **kwargs):
        return self.list(*args, **kwargs)

    @extend_schema(tags=("leaves",), description="Update a leaf")
    @action(detail=False, methods=["patch"], url_path="(?P<external_id>[^/.]+)/admin")
    def admin_update(self, *args, **kwargs):
        external_id = kwargs.get("external_id")
        leaf = Leaf.objects.get(external_id=external_id)
        serializer = LeafAdminSerializer(
            leaf,
            data=self.request.data,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
