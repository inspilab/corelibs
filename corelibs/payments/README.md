Setup
============

Define a `Payment` model by subclassing `payments.models.BasePayment`

    # mypaymentapp/models.py
    from decimal import Decimal

    from payments.models import BasePayment

    class Payment(BasePayment):

        def get_failure_url(self):
            return 'http://example.com/failure/'

        def get_success_url(self):
            return 'http://example.com/success/'

Configure your ``settings.py``

    # settings.py
    INSTALLED_APPS = [
        # ...
        'payments']

    PAYMENT_MODEL = 'mypaymentapp.Payment'
    PAYMENT_VARIANTS = {
        'default': ('payments.dummy.DummyProvider', {})}

  Note: Variants are named pairs of payment providers and their configuration.

Usage
============

#. Making a payment

Create a `Payment` instance:

    from decimal import Decimal
    from mypaymentapp.models import Payment

    # Init payment
    payment = Payment.objects.create(
        variant='default',  # this is the variant from PAYMENT_VARIANTS
        description='Book purchase',
        total=Decimal(120),
        currency='USD',
        billing_country_code='UK',
        customer_ip_address='127.0.0.1')

Authorization and capture:

    payment = get_object_or_404(Payment, token=token)
    provider = provider_factory(payment.variant)
    provider.process_data(payment, request)
