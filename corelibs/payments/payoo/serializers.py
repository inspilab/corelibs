from rest_framework import serializers
import stripe


class ResponseSerializer(serializers.Serializer):
    session = serializers.CharField(required=True)
    order_no = serializers.CharField(required=True)
    status = serializers.IntegerField(required=True)
    checksum = serializers.CharField(required=True)
