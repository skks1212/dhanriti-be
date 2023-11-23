from calendar import c
from rest_framework import serializers

from dhanriti.models.tanks import Canvas, Flow, Funnel, Tank
from django.db.models import Sum


class CanvasSerializer(serializers.ModelSerializer):
    funnels = serializers.SerializerMethodField()
    last_flows = serializers.SerializerMethodField()
    total_money = serializers.SerializerMethodField()

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
            "filled",
            "total_money"
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
    
    def get_total_money(self, obj):
        total_money = Tank.objects.filter(canvas=obj).aggregate(total_filled=Sum('filled'))['total_filled']
        total_money = (total_money or 0) + obj.filled
        return total_money


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
        return FunnelSerializer(obj.funnels.all(), many=True).data


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

class FunnelDetailSerializer(FunnelSerializer):
    in_tank = TankSerializer(read_only=True)

    class Meta(FunnelSerializer.Meta):
        fields = FunnelSerializer.Meta.fields + (
            "in_tank",
        )
        read_only_fields = FunnelSerializer.Meta.read_only_fields +  ("in_tank",)

class FlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flow
        fields = (
            "flowed",
            "external_id",
            "created_at",
            "modified_at",
            "meta",
            "manual"
        )
        read_only_fields = ("external_id", "created_at", "modified_at")

class FlowDetailSerializer(FlowSerializer):
    funnel = FunnelDetailSerializer(read_only=True)
    canvas = CanvasSerializer(read_only=True)

    class Meta(FlowSerializer.Meta):
        fields = FlowSerializer.Meta.fields + (
            "funnel",
            "canvas",
        )
        read_only_fields = FlowSerializer.Meta.read_only_fields + ("funnel", "canvas")