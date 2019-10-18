from __future__ import unicode_literals
import base64
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
try:
    from itertools import ifilter as filter
except ImportError:
    pass
import json
import logging

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils import timezone
import requests
from requests.exceptions import HTTPError

from .. import PaymentError, PaymentStatus, RedirectNeeded
from ..core import BasicProvider

CENTS = Decimal('0.01')


def authorize(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        self = args[0]
        payment = args[1]
        self.access_token = self._get_access_token(payment)
        try:
            response = fun(*args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 401:
                last_auth_response = self._get_last_response(
                    payment, is_auth=True)
                if 'access_token' in last_auth_response:
                    del last_auth_response['access_token']
                    self._set_response_data(
                        payment, last_auth_response, is_auth=True)
                self.access_token = self._get_access_token(payment)
                response = fun(*args, **kwargs)
            else:
                raise
        return response

    return wrapper


class PaypalAdapter(object):

    def _set_response_data(self, payment, response, is_auth=False):
        extra_data = json.loads(payment.extra_data or '{}')
        if is_auth:
            extra_data['auth_response'] = response
        else:
            extra_data['response'] = response
            if 'links' in response:
                extra_data['links'] = dict(
                    (link['rel'], link) for link in response['links'])
        payment.extra_data = json.dumps(extra_data)

    def _set_response_links(self, payment, response):
        transaction = response['transactions'][0]
        related_resources = transaction['related_resources'][0]
        resource_key = 'sale' if self._capture else 'authorize'
        links = related_resources[resource_key]['links']
        extra_data = json.loads(payment.extra_data or '{}')
        extra_data['links'] = dict((link['rel'], link) for link in links)
        payment.extra_data = json.dumps(extra_data)

    def _set_error_data(self, payment, error):
        extra_data = json.loads(payment.extra_data or '{}')
        extra_data['error'] = error
        payment.extra_data = json.dumps(extra_data)

    def _get_links(self, payment):
        extra_data = json.loads(payment.extra_data or '{}')
        links = extra_data.get('links', {})
        return links

    @authorize
    def _post(self, payment, *args, **kwargs):
        kwargs['headers'] = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token
        }
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])
        response = requests.post(*args, **kwargs)
        try:
            data = response.json()
        except ValueError:
            data = {}
        if 400 <= response.status_code <= 500:
            self._set_error_data(payment, data)
            message = 'Paypal error'
            if response.status_code == 400:
                error_data = response.json()
                message = error_data.get('message', message)

            payment.change_status(PaymentStatus.ERROR, message)
            raise PaymentError(message)
        else:
            self._set_response_data(payment, data)
        return data

    def _get_last_response(self, payment, is_auth=False):
        extra_data = json.loads(payment.extra_data or '{}')
        if is_auth:
            return extra_data.get('auth_response', {})
        return extra_data.get('response', {})

    def _basic_auth(self):
        """Find basic auth, and returns base64 encoded
        """
        credentials = "%s:%s" % (self.client_id, self.secret)
        return base64.b64encode(credentials.encode('utf-8')).decode('utf-8').replace("\n", "")

    def _get_access_token(self, payment):
        last_auth_response = self._get_last_response(payment, is_auth=True)
        created = payment.created
        now = timezone.now()
        if ('access_token' in last_auth_response and
                'expires_in' in last_auth_response and
                (created + timedelta(
                    seconds=last_auth_response['expires_in'])) > now):
            return '%s %s' % (last_auth_response['token_type'],
                              last_auth_response['access_token'])
        else:
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US',
                'Authorization': "Basic %s" % self._basic_auth()
            }
            post = {'grant_type': 'client_credentials'}
            response = requests.post(url=self.oauth2_url, data=post,
                                     headers=headers)
            response.raise_for_status()
            data = response.json()
            last_auth_response.update(data)
            self._set_response_data(payment, last_auth_response, is_auth=True)
            return '%s %s' % (data['token_type'], data['access_token'])

    def _get_transactions_items(self, payment):
        for purchased_item in payment.get_purchased_items():
            price = Decimal(purchased_item.price).quantize(
                CENTS, rounding=ROUND_HALF_UP)
            item = {
                'name': purchased_item.name[:127],
                'quantity': str(purchased_item.quantity),
                'price': str(price),
                'currency': purchased_item.currency,
                'sku': purchased_item.sku
            }
            yield item

    def _get_transactions_data(self, payment):
        items = list(self._get_transactions_items(payment))
        total = Decimal(payment.total).quantize(CENTS, rounding=ROUND_HALF_UP)
        data = {
            'intent': 'sale' if self._capture else 'authorize',
            'transactions': [
                {
                    'amount': {
                        'total': str(total),
                        'currency': payment.currency
                    },
                    'item_list': {'items': items},
                    'description': payment.description
                }
            ]
        }
        return data

    def _get_product_data(self, payment, extra_data=None):
        return_url = self._get_return_url(payment)
        cancel_url = self._get_cancel_url(payment)
        data = self._get_transactions_data(payment)
        data['redirect_urls'] = {'return_url': return_url, 'cancel_url': cancel_url}
        data['payer'] = {'payment_method': 'paypal'}
        return data

    def _create_payment(self, payment, extra_data=None):
        product_data = self._get_product_data(payment, extra_data)
        payment = self._post(payment, self.payments_url, data=product_data)
        return payment

    def _execute_payment(self, payment, payer_id):
        post = {'payer_id': payer_id}
        links = self._get_links(payment)
        if 'execute' in links and 'href' in links['execute']:
            execute_url = links['execute']['href']
        else:
            raise PaymentError('Cannot find link payment excute. Payment #%s' % payment.token)

        return self._post(payment, execute_url, data=post)

    def _get_amount_data(self, payment, amount=None):
        return {
            'currency': payment.currency,
            'total': str(amount.quantize(
                CENTS, rounding=ROUND_HALF_UP))}
