from __future__ import unicode_literals
from decimal import Decimal
import json

import stripe

from .. import (
    RedirectNeeded, PaymentError, PaymentStatus,
    get_payment_customer_model
)


class StripeAdapter(object):

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
