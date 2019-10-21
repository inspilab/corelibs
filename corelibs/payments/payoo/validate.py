from __future__ import unicode_literals
from decimal import Decimal
import json

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)
from .serializers import ResponseSerializer

import base64
import hashlib


class ValidateProvider(object):

    def _validate_process(self, payment, data):
        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')

        if payment.status == PaymentStatus.PREAUTH:
            raise PaymentError('This payment has already been processed.')

        if payment.total <= 0:
            raise PaymentError("Payment total must be greater than 0")

    def _validate_checksum_callback(self, data):
        # Validate input data
        serializer = ResponseSerializer(data=data)
        if not serializer.is_valid():
            raise PaymentError(serializer.errors)

        # Checksum
        session = serializer.validated_data['session']
        order_no = serializer.validated_data['order_no']
        status = serializer.validated_data['status']
        checksum = serializer.validated_data['checksum']

        str_hash = hashlib.sha512(
            (self.secret_key + session + '.' + order_no + '.' + status).encode()
        ).hexdigest()
        if not str_hash == checksum:
            raise PaymentError("Verified is failure. Order No: %s" % order_no)

        if not str(status) == '1':
            if 'errormsg' in data and data['errormsg']:
                raise PaymentError("Process payoo failed. Error: %s" % data['errormsg'])

    def _validate_checksum_ipn(self, data):
        # Validate input data
        encoded_product_data = data['PayooConnectionPackage']['Data']

        product_data = base64.b64encode(encoded_product_data.encode('utf-8')).decode('utf-8').replace("\n", "")
        checksum_data = data['PayooConnectionPackage']['Signature']
        keys = data['PayooConnectionPackage']['KeyFields']

        str_data = self.secret_key
        for k in keys:
            str_data += ('|' + product_data[k])

        str_hash = hashlib.sha512((str_data).encode()).hexdigest()
        if not str_hash == checksum:
            raise PaymentError("Verified is failure. Order No: %s" % product_data['order_no'])

        if 'State' in product_data and product_data['State'] != 'PAYMENT_RECEIVED':
            raise PaymentError("Process payoo failed. Error: %s" % product_data['State'])

    def _validate_capture(self, payment):
        pass
