from django.shortcuts import get_object_or_404
from dhanriti.models.payments import Payment
from dhanriti.models.tanks import Tank
from dhanriti.serializers.payments import PaymentsSerializer
from utils.views.base import BaseModelViewSet
from rest_framework import permissions
from rest_framework.serializers import ValidationError


class PaymentsViewSet(
    BaseModelViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    lookup_field = "external_id"

    def get_queryset(self):
        tank_external_id = self.kwargs.get("tank_external_id")
        return super().get_queryset().filter(tank__external_id=tank_external_id)

    def get_object(self):
        external_id = self.kwargs.get(self.lookup_field)
        obj = get_object_or_404(self.get_queryset(), external_id=external_id)
        return obj
    
    def perform_create(self, serializer):
        tank_external_id = self.kwargs.get("tank_external_id")
        tank = get_object_or_404(Tank, external_id=tank_external_id, canvas__user=self.request.user)

        if tank.filled < serializer.validated_data["amount"]:
            raise ValidationError("Payment amount is greater than tank filled amount")

        tank.filled -= serializer.validated_data["amount"]
        tank.save()

        serializer.save(tank=tank)
