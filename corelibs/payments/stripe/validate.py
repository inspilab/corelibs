from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)
from .serializers import CardSerializer


class ValidateProvider(object):

    def _validate_process(self, payment, data):
        # Validate payment
        if payment.transaction_id:
            raise PaymentError('This payment has already been processed.')

        if payment.status == PaymentStatus.CONFIRMED:
            raise PaymentError('This payment has already been confirmed.')

        if payment.status == PaymentStatus.PREAUTH:
            raise PaymentError('This payment has already been processed.')

        if payment.total <= 0:
            raise PaymentError("Payment total must be greater than 0")

        # Validate input
        card_data = data['card']
        serializer = CardSerializer(data=card_data)
        if not serializer.is_valid():
            raise PaymentError(serializer.errors)

    def _validate_capture(self, payment):
        pass
