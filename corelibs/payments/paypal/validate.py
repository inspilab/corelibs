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

        if not data.get('PayerID'):
            raise PaymentError("Cannot find PayerID. Payment: #%s" % payment.token)

    def _validate_capture(self, payment):
        pass
