from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.getIP import get_client_ip
from utils.views.base import BaseModelViewSetPlain
from utils.views.mixins import GetPermissionClassesMixin

from ..models import Search, Story, User
from ..serializers import SearchHistorySerializer, StorySerializer, UserSerializer


class SearchViewSet(GetPermissionClassesMixin, viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        query = request.query_params.get("query")
        if query is None:
            return Response(
                {"Status": "No search query provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stories = Story.objects.filter(
            (Q(title__icontains=query) | Q(genre__icontains=query))
            & Q(visibility__gt=1)
        )
        users = User.objects.filter(
            Q(username__icontains=query) | Q(full_name__icontains=query),
            account_setup=True,
        )

        story_serializer = StorySerializer(stories, many=True)
        user_serializer = UserSerializer(users, many=True)

        response_data = {
            "stories": story_serializer.data,
            "users": user_serializer.data,
        }

        return Response(response_data)


class SearchHistoryViewSet(
    BaseModelViewSetPlain,
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
):
    queryset = Search.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "external_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        query = self.request.data.get("query")
        search_ip = get_client_ip(self.request)
        user = self.request.user
        serializer.save(query=query, search_ip=search_ip, user=user)
        return super().perform_create(serializer)
