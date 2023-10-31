from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    h = serializers.IntegerField()
    w = serializers.IntegerField()
