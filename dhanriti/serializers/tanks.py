from calendar import c
from rest_framework import serializers

from dhanriti.models.tanks import Canvas, Flow, Funnel, Tank


class CanvasSerializer(serializers.ModelSerializer):
    funnels = serializers.SerializerMethodField()
    last_flows = serializers.SerializerMethodField()

    class Meta:
        model = Canvas
        fields = (
            "name",
            "description",
            "inflow",
            "inflow_rate",
            "last_flows",
            "funnels",
            "external_id",
            "created_at",
            "modified_at",
            "filled"
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "tanks")

    def save(self, **kwargs):
        user = self.context["request"].user
        self.validated_data["user"] = user
        return super().save(**kwargs)

    def get_funnels(self, obj):
        # get all funnels with in_tank = None

        funnels = Funnel.objects.filter(in_tank=None, out_tank__canvas=obj).order_by('-created_at')

        return FunnelSerializer(funnels, many=True).data
    
    def get_last_flows(self, obj):
        flows = Flow.objects.filter(canvas=obj, funnel=None).order_by('-created_at')[:5]
        return FlowSerializer(flows, many=True).data


class TankSerializer(serializers.ModelSerializer):
    funnels = serializers.SerializerMethodField()

    class Meta:
        model = Tank
        fields = (
            "name",
            "description",
            "capacity",
            "color",
            "external_id",
            "created_at",
            "modified_at",
            "funnels",
            "filled"
        )
        read_only_fields = ("external_id", "created_at", "modified_at")

    def get_funnels(self, obj):
        return FunnelSerializer(obj.in_tank.all(), many=True).data


class FunnelSerializer(serializers.ModelSerializer):
    out_tank = TankSerializer(read_only=True)
    last_flows = serializers.SerializerMethodField()

    class Meta:
        model = Funnel
        fields = (
            "name",
            "flow_rate",
            "flow_rate_type",
            "flow",
            "flow_type",
            "out_tank",
            "last_flows",
            "external_id",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "out_tank")

    def get_last_flows(self, obj):
        flows = Flow.objects.filter(funnel=obj).order_by('-created_at')[:5]
        return FlowSerializer(flows, many=True).data


class FlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flow
        fields = (
            "flowed",
            "external_id",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")