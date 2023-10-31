import re

from django.db.models import Q
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from utils.views.base import BaseModelViewSetPlain

from ..models import (
    User,
)
from ..permissions import IsSelfOrReadOnly
from ..serializers import (
    UserSerializer,
)


class UserViewSet(BaseModelViewSetPlain, RetrieveModelMixin, ListModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrReadOnly,)
    serializer_action_classes = {
        "list": UserSerializer,
        "retrieve": UserSerializer,
    }
    permission_action_classes = {
        "create": (permissions.AllowAny(),),
        "list": (permissions.IsAuthenticated(),),
        "retrieve": (permissions.AllowAny(),),
    }

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
