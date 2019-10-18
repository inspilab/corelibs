from __future__ import unicode_literals
import re
try:
    from urllib.parse import urljoin, urlencode
except ImportError:
    from urllib import urlencode
    from urlparse import urljoin
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


PAYMENT_VARIANTS = {'default': ('payments.bank.BankProvider', {})}


class BasicProvider(object):
    '''
    This class defines the provider API. It should not be instantiated
    directly. Use factory instead.
    '''
    _method = 'post'

    def __init__(self, currency_code, coefficient, capture=True):
        self._coefficient = coefficient
        self._currency_code = currency_code
        self._capture = capture

    def session_start(self, payment, data=None):
        raise NotImplementedError()

    def preprocess_data(self, request, option=None):
        '''
        Preprocess parse request.data to validated_data.
        '''
        raise NotImplementedError()

    def process_data(self, payment, data):
        '''
        Process callback request from a payment provider.
        '''
        raise NotImplementedError()

    def get_return_url(self, payment, extra_data=None):
        payment_link = payment.get_process_url()
        url = payment_link
        if extra_data:
            qs = urlencode(extra_data)
            return url + '?' + qs
        return url

    def get_cancel_url(self, payment, extra_data=None):
        payment_link = payment.get_failure_url()
        url = payment_link
        if extra_data:
            qs = urlencode(extra_data)
            return url + '?' + qs
        return url

    def capture(self, payment, amount=None):
        raise NotImplementedError()

    def release(self, payment):
        raise NotImplementedError()

    def refund(self, payment, amount=None):
        raise NotImplementedError()


class ProviderFactory(object):

    @staticmethod
    def get_provider(variant, currency_code, coefficient):
        variants = getattr(settings, 'PAYMENT_VARIANTS', PAYMENT_VARIANTS)
        handler, config = variants.get(variant, (None, None))
        if not handler:
            raise ValueError('Payment variant does not exist: %s' %  (variant,))

        module_path, class_name = handler.rsplit('.', 1)
        module = __import__(
            str(module_path), globals(), locals(), [str(class_name)])
        class_ = getattr(module, class_name)
        provider = class_(**config, currency_code=currency_code, coefficient=coefficient)
        return provider
