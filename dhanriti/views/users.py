import re

from django.db.models import Count, Exists, OuterRef, Q
from django.http import Http404
from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    OrderingFilter,
)
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response

from utils.pagination import CustomLimitOffsetPagination
from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import PartialUpdateModelMixin
from dhanriti.models.misc import Invite
from dhanriti.serializers.users import UserAdminSerializer, UserPublicSerializer

from ..models import (
    Follow,
    Leaf,
    Shelf,
    ShelfLeaf,
    ShelfStory,
    Story,
    User,
    VisibilityType,
)
from ..permissions import IsSelfOrReadOnly
from ..serializers import (
    ShelfDetailSerializer,
    ShelfSerializer,
    UserDetailSerializer,
    UserSerializer,
)


class UserFilter(FilterSet):
    name = CharFilter(method="filter_by_name")
    username = CharFilter(field_name="username", lookup_expr="icontains")
    email = CharFilter(field_name="email", lookup_expr="icontains")
    account_setup = BooleanFilter(field_name="account_setup", lookup_expr="exact")
    closed_beta = BooleanFilter(field_name="closed_beta", lookup_expr="exact")
    invite_sent = BooleanFilter(method="filter_by_invite_sent")
    is_bot = BooleanFilter(field_name="is_bot", lookup_expr="exact")
    order_by = OrderingFilter(
        fields=(
            ("followers", "followers"),
            ("following", "following"),
            ("story", "story"),
        ),
        field_labels={
            "followers": "Followers",
            "following": "Following",
            "story": "StoryCount",
        },
    )

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) | Q(username__icontains=value)
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.form.cleaned_data.get("order_by"):
            for field in self.form.cleaned_data.get("order_by"):
                if field in ["followers", "-followers"]:
                    queryset = queryset.annotate(
                        followers_count=Count("followers")
                    ).order_by(
                        "-followers_count" if field[0] == "-" else "followers_count",
                        "-preference_points",
                    )

                elif field in ["following", "-following"]:
                    queryset = queryset.annotate(
                        following_count=Count("following")
                    ).order_by(
                        "-following_count" if field[0] == "-" else "following_count",
                        "-preference_points",
                    )

                elif field in ["story", "-story"]:
                    queryset = queryset.annotate(story_count=Count("story")).order_by(
                        "-story_count" if field[0] == "-" else "story_count",
                        "-preference_points",
                    )
        return queryset

    def filter_by_invite_sent(self, queryset, name, value):
        if value is not None:
            invite = Invite.objects.filter(user=OuterRef("pk"))
            queryset = queryset.annotate(invite_sent=Exists(invite)).filter(
                invite_sent=value
            )

        return queryset


class UserAdminFilter(FilterSet):
    name = CharFilter(method="filter_by_name")
    email = CharFilter(method="filter_by_email")
    account_setup = CharFilter(method="filter_by_account_setup")
    closed_beta = CharFilter(method="filter_by_closed_beta")


class UserViewSet(BaseModelViewSetPlain, RetrieveModelMixin, ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsSelfOrReadOnly,)
    serializer_action_classes = {
        "list": UserSerializer,
        "retrieve": UserPublicSerializer,
        "admin": UserAdminSerializer,
    }
    permission_action_classes = {
        "create": (permissions.AllowAny(),),
        "list": (permissions.IsAuthenticated(),),
        "retrieve": (permissions.AllowAny(),),
        "follow": (permissions.IsAuthenticated(),),
        "unfollow": (permissions.IsAuthenticated(),),
        "upload_callback": (permissions.AllowAny,),
        "followers": (permissions.AllowAny(),),
        "following": (permissions.AllowAny(),),
        "admin": (permissions.IsAdminUser(),),
    }
    filterset_class = UserFilter
    lookup_field = "username"

    def get_queryset(self):
        queryset = super().get_queryset()

        name_query = self.request.query_params.get("name")
        username_query = self.request.query_params.get("username")

        if self.action == "list":
            queryset = queryset.filter(~Q(username__startswith="VISHNU-DEFAULT-"))
            if not name_query and not username_query:
                queryset = queryset.filter(preference_points__gte=0)

            queryset = queryset.distinct().order_by("-preference_points")

        return queryset

    def get_object(self):
        return (
            super().get_object()
            if self.kwargs.get(self.lookup_field)
            else self.get_queryset().get(pk=self.request.user.id)
        )

    def destroy(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    @extend_schema(tags=("users",), request=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["post"])
    def follow(self, *args, **kwargs):
        # prevent user from following themselves
        if self.get_object() == self.request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not Follow.objects.filter(
            follower=self.request.user,
            followed=self.get_object(),
        ).exists():
            Follow.objects.create(
                follower=self.request.user,
                followed=self.get_object(),
            )
            return Response(status=status.HTTP_200_OK)
        raise ValidationError({"detail": "You already follow this user"})

    @extend_schema(tags=("users",), request=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["post"])
    def unfollow(self, *args, **kwargs):
        # prevent user from unfollowing themselves
        if self.get_object() == self.request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            Follow.objects.get(
                follower=self.request.user,
                followed=self.get_object(),
            ).delete()
            return Response(status=status.HTTP_200_OK)
        except Follow.DoesNotExist as e:
            raise ValidationError({"detail": "You don't follow this user"}) from e

    @extend_schema(tags=("users",), request=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["get"])
    def followers(self, *args, **kwargs):
        user = self.get_object()
        follower_ids = user.followers.values_list("follower", flat=True)
        followers = User.objects.filter(id__in=follower_ids)
        paginator = CustomLimitOffsetPagination()
        paginated_followers = paginator.paginate_queryset(followers, self.request)
        serializer = UserSerializer(paginated_followers, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(tags=("users",), request=None, responses={status.HTTP_200_OK: None})
    @action(detail=True, methods=["get"])
    def following(self, *args, **kwargs):
        user = self.get_object()
        following_ids = user.following.values_list("followed", flat=True)
        following = User.objects.filter(id__in=following_ids)
        paginator = CustomLimitOffsetPagination()
        paginated_following = paginator.paginate_queryset(following, self.request)
        serializer = UserSerializer(paginated_following, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False)
    def me(self, *args, **kwargs):
        """Get current user"""
        return super().retrieve(*args, **kwargs)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        """Update current user"""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def setup(self, request, *args, **kwargs):
        user = self.request.user
        username = request.data.get("username")

        if not user.account_setup and username == user.username:
            user.account_setup = True
            user.save()
            return Response(status=status.HTTP_200_OK)

        # check if username is taken
        if User.objects.filter(username=username).exists():
            return Response(
                {"username": "Username is already taken"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if username != username.lower():
            return Response(
                {"username": "Username must be lowercase"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if username is max 20 characters
        if len(username) > 20:
            return Response(
                {"username": "Username must be max 20 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if username has only numbers,letters or hyphens
        if not re.match("^[a-zA-Z0-9-]*$", username):
            return Response(
                {"username": "Username must contain only numbers, letters or hyphens"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if username is atleast 3 characters
        if len(username) < 3:
            return Response(
                {"username": "Username must be atleast 3 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if username does not start or end with hyphen
        if username[0] == "-" or username[-1] == "-":
            return Response(
                {"username": "Username must not start or end with hyphen"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # username should not start with VISHNU-DEFAULT-
        if username.startswith("VISHNU-DEFAULT-"):
            return Response(
                {"username": "Username must not start with VISHNU-DEFAULT-"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if user's username starts with "VISHNU-DEFAULT"
        if not user.account_setup:
            user.username = username
            user.account_setup = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def admin(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["patch"], url_path="(?P<external_id>[^/.]+)/admin")
    def admin_update(self, request, *args, **kwargs):
        external_id = kwargs.get("external_id")
        user = User.objects.get(external_id=external_id)
        serializer = UserAdminSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ShelfViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    PartialUpdateModelMixin,
):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer
    lookup_url_kwarg = "shelf_id"
    permission_classes = (permissions.IsAuthenticated,)
    permission_action_classes = {
        "list": (permissions.AllowAny(),),
        "retrieve": (permissions.AllowAny(),),
    }
    serializer_action_classes = {
        "list": ShelfDetailSerializer,
    }

    def get_queryset(self):
        user = self.kwargs.get("user_username")

        queryset = self.queryset.filter(user__username=user)

        if self.request.user.is_authenticated and self.request.user.username == user:
            return queryset

        if self.action == "list":
            queryset = queryset.filter(visibility__gte=VisibilityType.PUBLIC)
        else:
            queryset = queryset.filter(visibility__gte=VisibilityType.UNLISTED)

        return queryset

    def get_object(self):
        try:
            return self.queryset.get(
                external_id=self.kwargs.get("shelf_id"),
                user__username=self.kwargs.get("user_username"),
            )
        except Shelf.DoesNotExist as e:
            raise Http404 from e

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if (
            instance.visibility == VisibilityType.PRIVATE
            and instance.user != request.user
        ):
            raise Http404
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if self.kwargs.get("user_username") != self.request.user.username:
            raise PermissionDenied(
                {"detail": "You can't create a shelf for another user"}
            )
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.kwargs.get("user_username") != self.request.user.username:
            raise PermissionDenied(
                {"detail": "You can't update a shelf for another user"}
            )
        serializer.save(user=self.request.user)
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if self.kwargs.get("user_username") != self.request.user.username:
            raise PermissionDenied(
                {"detail": "You can't delete a shelf for another user"}
            )
        return super().perform_destroy(instance)

    @extend_schema(
        tags=("shelves",), request=None, responses={status.HTTP_200_OK: None}
    )
    @action(detail=True, methods=["post"])
    def add_or_remove(self, *args, **kwargs):
        shelf = self.get_object()
        story_id = self.request.data.get("story_id")
        leaf_id = self.request.data.get("leaf_id")

        if self.kwargs.get("user_username") == self.request.user.username:
            if not story_id and not leaf_id:
                raise ValidationError({"detail": "story_id or leaf_id is required"})

            elif story_id:
                story = Story.objects.get(
                    external_id=story_id, visibility__gte=VisibilityType.UNLISTED
                )
                if not story:
                    raise ValidationError({"detail": "story_id is invalid"})
                if shelf.stories.filter(external_id=story_id).exists():
                    ShelfStory.objects.filter(shelf=shelf, story=story).delete()
                else:
                    ShelfStory.objects.create(shelf=shelf, story=story)

            elif leaf_id:
                leaf = Leaf.objects.get(
                    external_id=leaf_id, visibility__gte=VisibilityType.UNLISTED
                )
                if not leaf:
                    raise ValidationError({"detail": "leaf_id is invalid"})
                if shelf.leaves.filter(external_id=leaf_id).exists():
                    ShelfLeaf.objects.filter(shelf=shelf, leaf=leaf).delete()
                else:
                    ShelfLeaf.objects.create(shelf=shelf, leaf=leaf)

            return super().retrieve(*args, **kwargs)

        raise PermissionDenied(
            {"detail": "You can't add or remove a story or leaf for another user"}
        )
