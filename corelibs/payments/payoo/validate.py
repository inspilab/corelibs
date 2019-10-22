from __future__ import unicode_literals
from decimal import Decimal
import json

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)

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

    def _validate_capture(self, payment):
        pass
