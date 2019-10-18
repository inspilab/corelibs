from __future__ import unicode_literals
from decimal import Decimal
import json

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)


class ValidateProvider(object):

    def _validate_process(self, payment, data):
        if payment.bid:
            raise PaymentError("Cart #%s has been converted" % payment.cart_id)

        if payment.total <= 0:
            raise PaymentError("Payment total must be greater than 0")

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

    def _validate_capture(self, payment):
        pass
