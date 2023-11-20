from calendar import c
from rest_framework import serializers

from dhanriti.models.tanks import Canvas, Flow, Funnel, Tank


class CanvasSerializer(serializers.ModelSerializer):
    funnels = serializers.SerializerMethodField()

    class Meta:
        model = Canvas
        fields = (
            "name",
            "description",
            "inflow",
            "inflow_rate",
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

        funnels = Funnel.objects.filter(in_tank=None, out_tank__canvas=obj).order_by('created_at')

        return FunnelSerializer(funnels, many=True).data


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

    class Meta:
        model = Funnel
        fields = (
            "name",
            "flow_rate",
            "flow_rate_type",
            "flow",
            "flow_type",
            "out_tank",
            "external_id",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "out_tank")


class FlowSerializer(serializers.ModelSerializer):
    funnel = FunnelSerializer(read_only=True)

    class Meta:
        model = Flow
        fields = (
            "funnel",
            "flowed",
            "external_id",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at")