from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin

from utils.views.base import BaseModelViewSetPlain

from ..models import Report
from ..serializers import ReportSerializer


class ReportViewSet(
    BaseModelViewSetPlain, CreateModelMixin, RetrieveModelMixin, ListModelMixin
):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    lookup_field = "external_id"
    permission_classes = ()
    permission_action_classes = {
        "create": (permissions.AllowAny(),),
        "list": (permissions.IsAuthenticated(),),
        "retrieve": (permissions.IsAuthenticated(),),
    }

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        super().perform_create(serializer)
