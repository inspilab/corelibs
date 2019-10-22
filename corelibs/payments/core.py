from __future__ import unicode_literals
import re
try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import urljoin
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from . import get_payment_method_model

PAYMENT_VARIANTS = {'default': ('payments.bank.BankProvider', {})}


class BasicProvider(object):
    '''
    This class defines the provider API. It should not be instantiated
    directly. Use factory instead.
    '''
    _method = 'post'

    def __init__(self, currency_code, coefficient, capture=True):
        if not coefficient or coefficient <= 0:
            raise Exception("Coefficient is invalid")

        self._coefficient = coefficient
        self._currency_code = currency_code
        self._capture = capture

    def _get_return_url(self, payment, extra_data=None):
        payment_link = payment.get_return_url()
        url = payment_link
        if extra_data:
            qs = urlencode(extra_data)
            return url + '?' + qs
        return url

    def _get_ipn_url(self, payment, extra_data=None):
        payment_link = payment.get_ipn_url()
        url = payment_link
        if extra_data:
            qs = urlencode(extra_data)
            return url + '?' + qs
        return url

    def _get_cancel_url(self, payment, extra_data=None):
        payment_link = payment.get_cancel_url()
        url = payment_link
        if extra_data:
            qs = urlencode(extra_data)
            return url + '?' + qs
        return url

    def transform_data(self, request):
        raise NotImplementedError()

    def on_waiting(self, payment, data=None):
        raise NotImplementedError()

    def process(self, payment, data):
        raise NotImplementedError()

    def capture(self, payment, amount=None):
        raise NotImplementedError()

    def release(self, payment):
        raise NotImplementedError()

    def refund(self, payment, amount=None):
        raise NotImplementedError()


class ProviderFactory(object):

    @staticmethod
    def get_provider(variant, currency_code):
        PaymentMethod = get_payment_method_model()
        method = PaymentMethod.objects.filter(
            payment_method=variant, currency=currency_code, is_active=True
        ).first()
        if not method or not method.coefficient or method.coefficient <= 0:
            raise ValueError('Payment variant does not exist: %s' %  (variant,))

        variants = getattr(settings, 'PAYMENT_VARIANTS', PAYMENT_VARIANTS)
        handler, config = variants.get(variant, (None, None))
        if not handler:
            raise ValueError('Payment variant does not exist: %s' %  (variant,))

        module_path, class_name = handler.rsplit('.', 1)
        module = __import__(
            str(module_path), globals(), locals(), [str(class_name)])
        class_ = getattr(module, class_name)
        provider = class_(
            **config, currency_code=currency_code, coefficient=method.coefficient)
        return provider
