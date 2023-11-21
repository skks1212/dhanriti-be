from django.shortcuts import get_object_or_404
from dhanriti.models.tanks import Canvas, Flow, Funnel
from dhanriti.serializers.tanks import (
    FlowDetailSerializer,
    FlowSerializer,
)
from dhanriti.tasks.flow import trigger_canvas_inflow, trigger_funnel_flow
from utils.views.base import BaseModelViewSetPlain
from django_filters.rest_framework import (
    FilterSet,
)
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

class FlowFilter(FilterSet):
    class Meta:
        model = Flow
        fields = {
            "canvas__external_id": ["exact"],
            "funnel__out_tank__external_id": ["exact"],
            "funnel__in_tank__external_id": ["exact"],
            "funnel__external_id": ["exact"],
            "flowed": ["exact", "lte", "gte"],
            "created_at": ["exact", "lte", "gte"],
            "modified_at": ["exact", "lte", "gte"],
        }


class FlowViewSet(
    BaseModelViewSetPlain,
    ListModelMixin,
    RetrieveModelMixin,
):
    queryset = Flow.objects.all()
    serializer_class = FlowDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_class = FlowFilter

    lookup_field = "external_id"

    def get_queryset(self):
        canvas_external_id = self.kwargs.get("canvas_external_id")
        return super().get_queryset().filter(canvas__external_id=canvas_external_id)

    def get_object(self):
        external_id = self.kwargs.get(self.lookup_field)

        obj = get_object_or_404(self.get_queryset(), external_id=external_id)
        return obj
    
    @action(methods=["POST"], detail=False)
    def trigger(self, *args, **kwargs):
        canvas_external_id = self.kwargs.get("canvas_external_id")
        canvas = get_object_or_404(Canvas, external_id=canvas_external_id)
        funnel_external_id = self.request.query_params.get('funnel_external_id')
        if funnel_external_id:
            funnel = get_object_or_404(Funnel, external_id=funnel_external_id)
            print("triggering flow for funnel")
            print(funnel)
            trigger_funnel_flow(funnel, bypass_last_flow=True, manual_trigger=True)
        else:
            print("triggering flow for canvas")
            print(canvas)
            trigger_canvas_inflow(canvas, manual_trigger=True)
        
        return Response(status=status.HTTP_201_CREATED)