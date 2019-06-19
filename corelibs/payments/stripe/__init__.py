from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)
from ..core import BasicProvider
from .serializers import CardSerializer


class StripeProvider(BasicProvider):

    def __init__(self, public_key, secret_key, image='', name='', **kwargs):
        stripe.api_key = secret_key
        self.secret_key = secret_key
        self.public_key = public_key
        self.image = image
        self.name = name
        self.charge = None
        super(StripeProvider, self).__init__(**kwargs)

    def get_form(self, payment, data=None):
        if payment.status == PaymentStatus.WAITING:
            payment.change_status(PaymentStatus.INPUT)

        # Stay in page
        return True

    def process_data(self, payment, request):
        success_url = payment.get_success_url()
        if not payment.transaction_id:
            stripe.api_key = self.secret_key
            try:
                # Validate card
                card_data = request.data['card']
                serializer = CardSerializer(data=card_data)
                serializer.is_valid(raise_exception=True)
                # Update customer info
                token = stripe.Token.create(card=serializer.validated_data)
                customer, error = self._create_or_update_customer(
                    email=request.user.email, method='stripe', token_id=token.id
                )
                if error:
                    raise Exception("Update customer failed", error)

                coefficient = self.get_coefficient(currency_code=payment.currency)
                self.charge = stripe.Charge.create(
                    capture=False,
                    amount=int(payment.total) * int(coefficient),
                    currency=payment.currency,
                    customer=customer.customer_id)
            except Exception as e:
                error_message = str(e)
                raise PaymentError(error_message)
        else:
            raise PaymentError('This payment has already been processed.')

        payment.transaction_id = self.charge.id
        payment.attrs.charge = json.dumps(self.charge)
        payment.change_status(PaymentStatus.PREAUTH)
        if self._capture:
            payment.capture()
        return success_url

    def capture(self, payment, amount=None):
        coefficient = self.get_coefficient(currency_code=payment.currency)
        amount = int(amount or payment.total) * int(coefficient)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        try:
            charge.capture(amount=amount)
        except stripe.InvalidRequestError as e:
            payment.change_status(PaymentStatus.REFUNDED)
            raise PaymentError('Payment already refunded')
        payment.attrs.capture = json.dumps(charge)
        return Decimal(amount) / int(coefficient)

    def release(self, payment):
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund()
        payment.attrs.release = json.dumps(charge)

    def refund(self, payment, amount=None):
        coefficient = self.get_coefficient(currency_code=payment.currency)
        amount = int(amount or payment.total) * int(coefficient)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund(amount=amount)
        payment.attrs.refund = json.dumps(charge)
        return Decimal(amount) / int(coefficient)

    def _create_or_update_customer(self, email, method, token_id):
        stripe.api_key = self.secret_key
        PaymentCustomer = get_payment_customer_model()

        instance = PaymentCustomer.objects.filter(email=email, method=method).first()
        if not instance:
            # Create
            try:
                stripe_customer = stripe.Customer.create(
                    email=email, source=token_id
                )
                instance = PaymentCustomer.objects.create(
                    email=email,
                    method=method,
                    customer_id=stripe_customer.id
                )
            except Exception as error:
                return instance, error
        else:
            # Update
            try:
                card = stripe.Customer.create_source(
                    instance.customer_id,
                    source=token_id
                )
                if not card or not card.id:
                    raise Exception(
                        "Cannot attach card to customer %s. Token: %s" % (
                            instance.customer_id, token_id
                        )
                    )
                stripe.Customer.modify(
                    instance.customer_id,
                    default_source=card.id
                )
            except Exception as error:
                return instance, error

        return instance, ''

