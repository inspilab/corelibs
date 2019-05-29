from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import RedirectNeeded, PaymentError, PaymentStatus
from ..core import BasicProvider


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
            payment.save()

        # Stay in page
        return True

    def process_data(self, payment, request):
        success_url = payment.get_success_url()
        if not payment.transaction_id:
            stripe.api_key = self.provider.secret_key
            try:
                self.charge = stripe.Charge.create(
                    capture=False,
                    amount=int(payment.total * 100),
                    currency=payment.currency,
                    card=request.data['card'],
                    description='%s %s' % (
                        payment.billing_last_name,
                        payment.billing_first_name))
            except stripe.error.CardError as e:
                # Making sure we retrieve the charge
                charge_id = e.json_body['error']['charge']
                self.charge = stripe.Charge.retrieve(charge_id)
                # The card has been declined
                self._errors['__all__'] = self.error_class([str(e)])
                payment.change_status(PaymentStatus.ERROR, str(e))
        else:
            msg = _('This payment has already been processed.')
            self._errors['__all__'] = self.error_class([msg])

        payment.transaction_id = self.charge.id
        payment.attrs.charge = json.dumps(self.charge)
        payment.change_status(PaymentStatus.PREAUTH)
        if self.provider._capture:
            payment.capture()
        return success_url

    def capture(self, payment, amount=None):
        amount = int((amount or payment.total) * 100)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        try:
            charge.capture(amount=amount)
        except stripe.InvalidRequestError as e:
            payment.change_status(PaymentStatus.REFUNDED)
            raise PaymentError('Payment already refunded')
        payment.attrs.capture = json.dumps(charge)
        return Decimal(amount) / 100

    def release(self, payment):
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund()
        payment.attrs.release = json.dumps(charge)

    def refund(self, payment, amount=None):
        amount = int((amount or payment.total) * 100)
        charge = stripe.Charge.retrieve(payment.transaction_id)
        charge.refund(amount=amount)
        payment.attrs.refund = json.dumps(charge)
        return Decimal(amount) / 100
