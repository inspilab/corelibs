from rest_framework import serializers
import stripe


class OrderSerializer(serializers.Serializer):
    order_no = serializers.CharField(required=True)
    order_cash_amount = serializers.IntegerField(required=True)
    order_ship_date = serializers.DateField(required=True, format='%Y-%m-%d')
    order_detail = serializers.CharField(required=True)
    customer_name = serializers.CharField(required=True)
    customer_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer_email = serializers.EmailField(required=True)


class ResponseSerializer(serializers.Serializer):
    session = serializers.CharField(required=True)
    order_no = serializers.CharField(required=True)
    status = serializers.IntegerField(required=True)
    checksum = serializers.CharField(required=True)
