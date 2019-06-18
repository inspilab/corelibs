from rest_framework import serializers
import stripe


class CardSerializer(serializers.Serializer):
    number = serializers.CharField(required=True)
    exp_month = serializers.CharField(required=True)
    exp_year = serializers.CharField(required=True)
    cvc = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    address_country = serializers.CharField(max_length=2, required=True)
