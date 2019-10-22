from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)
from ..core import BasicProvider
from .validate import ValidateProvider
from .adapter import StripeAdapter


class StripeProvider(BasicProvider, ValidateProvider, StripeAdapter):

    def __init__(self, public_key, secret_key, image='', name='', **kwargs):
        stripe.api_key = secret_key
        self.secret_key = secret_key
        self.public_key = public_key
        self.image = image
        self.name = name
        self.charge = None
        super(StripeProvider, self).__init__(**kwargs)

    def on_waiting(self, payment, data=None):
        payment.change_status(PaymentStatus.WAITING)
        return True

    def transform_data(self, request):
        data = request.data.copy()
        data['user_email'] = request.user.email
        return data

    def process(self, payment, data):
        self._validate_process(payment, data)
        stripe.api_key = self.secret_key

        try:
            # Update customer info
            customer = self._create_or_update_customer(data['user_email'], data['card'])
            amount_charge = int(payment.total * self._coefficient)
            if self._capture:
                self.charge = stripe.Charge.create(
                    capture=True, amount=amount_charge,
                    currency=payment.currency, customer=customer.customer_id
                )
                payment.captured_amount = payment.total
                payment.change_status(PaymentStatus.CONFIRMED)
            else:
                self.charge = stripe.Charge.create(
                    capture=False, amount=amount_charge,
                    currency=payment.currency, customer=customer.customer_id
                )
                payment.change_status(PaymentStatus.PREAUTH)

        except Exception as e:
            error_message = str(e)
            raise PaymentError(error_message)

        payment.transaction_id = self.charge.id
        payment.attrs.charge = json.dumps(self.charge)
        return payment.get_success_url()

    def capture(self, payment, amount=None):
        self._validate_capture(payment)

        amount = int((amount or payment.total) * self._coefficient)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        try:
            charge.capture(amount=amount)
        except stripe.InvalidRequestError as e:
            payment.change_status(PaymentStatus.REFUNDED)
            raise PaymentError('Payment already refunded')
        payment.attrs.capture = json.dumps(charge)
        return Decimal(amount) / self._coefficient

    def release(self, payment):
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund()
        payment.attrs.release = json.dumps(charge)

    def refund(self, payment, amount=None):
        amount = int((amount or payment.total) * self._coefficient)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund(amount=amount)
        payment.attrs.refund = json.dumps(charge)
        return Decimal(amount) / self._coefficient
