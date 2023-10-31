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
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "tanks")

    def save(self, **kwargs):
        user = self.context["request"].user
        self.validated_data["user"] = user
        return super().save(**kwargs)

    def get_funnels(self, obj):
        # get all funnels with in_tank = None

        funnels = Funnel.objects.filter(in_tank=None, out_tank__canvas=obj)

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
        )
        read_only_fields = ("external_id", "created_at", "modified_at")

    def get_funnels(self, obj):
        return FunnelSerializer(obj.in_tank.all(), many=True).data


class FunnelSerializer(serializers.ModelSerializer):
    out_tank = TankSerializer(read_only=True)
    out_tank_external_id = serializers.CharField()
    in_tank_external_id = serializers.CharField(required=False)

    class Meta:
        model = Funnel
        fields = (
            "name",
            "flow_rate",
            "flow_rate_type",
            "flow",
            "flow_type",
            "out_tank",
            "out_tank_external_id",
            "in_tank_external_id",
            "external_id",
            "created_at",
            "modified_at",
        )
        read_only_fields = ("external_id", "created_at", "modified_at", "out_tank")
        write_only_fields = ("out_tank_external_id", "in_tank_external_id")

    def validate(self, data):
        out_tank_external_id = data.get("out_tank_external_id")
        in_tank_external_id = data.get("in_tank_external_id")

        if out_tank_external_id == in_tank_external_id:
            raise serializers.ValidationError("Out tank and in tank cannot be same")

        return data

    def save(self, **kwargs):
        in_tank_external_id = self.validated_data.get("in_tank_external_id")
        out_tank_external_id = self.validated_data.get("out_tank_external_id")
        user = self.context["request"].user

        if in_tank_external_id:
            in_tank = Tank.objects.get(
                external_id=in_tank_external_id, canvas__user=user
            )
            self.validated_data["in_tank"] = in_tank

        out_tank = Tank.objects.get(external_id=out_tank_external_id, canvas__user=user)

        self.validated_data["out_tank"] = out_tank

        self.validated_data.pop("out_tank_external_id")
        self.validated_data.pop("in_tank_external_id", None)

        return super().save(**kwargs)


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
