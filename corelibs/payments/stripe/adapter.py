from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)


class StripeAdapter(object):

    def _create_or_update_customer(self, email, card_data):
        stripe.api_key = self.secret_key
        PaymentCustomer = get_payment_customer_model()

        token = stripe.Token.create(card=card_data)
        instance = PaymentCustomer.objects.filter(email=email, method='stripe').first()
        if not instance:
            # Create
            stripe_customer = stripe.Customer.create(email=email, source=token.id)
            instance = PaymentCustomer.objects.create(
                email=email, method='stripe', customer_id=stripe_customer.id
            )
        else:
            card = stripe.Customer.create_source(instance.customer_id, source=token.id)
            stripe.Customer.modify(instance.customer_id, default_source=card.id)

        return instance
