import base64
import hashlib

from rest_framework import serializers
from django.core.exceptions import ValidationError


class ShopbackSerializer(serializers.Serializer):
    secret_key = serializers.CharField(required=True)
    session = serializers.CharField(required=True)
    order_no = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    checksum = serializers.CharField(required=True)
    errorcode = serializers.CharField(required=False, allow_blank=True)
    errormsg = serializers.CharField(required=False, allow_blank=True)

    def run_validation(self, data):
        data = super(ShopbackSerializer, self).run_validation(data)

        # Checksum
        secret_key = data['secret_key']
        session = data['session']
        order_no = data['order_no']
        status = data['status']
        checksum = data['checksum']

        str_hash = hashlib.sha512(
            (secret_key + session + '.' + order_no + '.' + status).encode()
        ).hexdigest()

        if not str_hash == checksum:
            raise ValidationError("Verified is failure. Order No: %s" % order_no)

        if not str(status) == '1':
            raise ValidationError("Process payoo failed. Error: %s" % data.get('errormsg'))
