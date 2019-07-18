from rest_framework import serializers


class NotificationSerializer(serializers.Serializer):
    event = serializers.CharField(required=True)
    data = serializers.JSONField(required=True)
    target = serializers.EmailField(required=True)
    language = serializers.CharField(required=False)
