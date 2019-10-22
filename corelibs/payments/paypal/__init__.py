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
from .adapter import PaypalAdapter
from .validate import ValidateProvider


class PaypalProvider(BasicProvider, ValidateProvider, PaypalAdapter):
    '''
    paypal.com payment provider
    '''
    def __init__(self, client_id, secret,
                 endpoint='https://api.sandbox.paypal.com', **kwargs):
        self.secret = secret
        self.client_id = client_id
        self.endpoint = endpoint
        self.oauth2_url = str(self.endpoint) + '/v1/oauth2/token'
        self.payments_url = str(self.endpoint) + '/v1/payments/payment'
        self.payment_execute_url = str(self.payments_url) + '/%(id)s/execute/'
        self.payment_refund_url = (
            str(self.endpoint) + '/v1/payments/capture/{captureId}/refund')
        super(PaypalProvider, self).__init__(**kwargs)

    def transform_data(self, request):
        data = request.data.copy()
        return data

    def on_waiting(self, payment, data=None):
        if not payment.id:
            payment.save()
        links = self._get_links(payment)
        redirect_to = links.get('approval_url')
        if not redirect_to:
            payment_data = self._create_payment(payment)
            payment.transaction_id = payment_data['id']
            links = self._get_links(payment)
            redirect_to = links['approval_url']
        payment.change_status(PaymentStatus.WAITING)
        raise RedirectNeeded(redirect_to['href'])

    def process(self, payment, data):
        # Validate
        self._validate_process(payment, data)

        # Process
        success_url = payment.get_success_url()
        payer_id = data.get('PayerID')

        executed_payment = self._execute_payment(payment, payer_id)
        self._set_response_links(payment, executed_payment)
        if 'payer' in executed_payment and 'payer_info' in executed_payment['payer']:
            payment.attrs.payer_info = executed_payment['payer']['payer_info']
        if self._capture:
            payment.captured_amount = payment.total
            payment.change_status(PaymentStatus.CONFIRMED)
        else:
            payment.change_status(PaymentStatus.PREAUTH)
        return success_url

    def capture(self, payment, amount=None):
        if amount is None:
            amount = payment.total
        amount_data = self._get_amount_data(payment, amount)
        capture_data = {
            'amount': amount_data,
            'is_final_capture': True
        }
        links = self._get_links(payment)
        url = links['capture']['href']
        try:
            capture = self._post(payment, url, data=capture_data)
        except HTTPError as e:
            try:
                error = e.response.json()
            except ValueError:
                error = {}
            if error.get('name') != 'AUTHORIZATION_ALREADY_COMPLETED':
                raise e
            capture = {'state': 'completed'}
        state = capture['state']
        if state == 'completed':
            payment.change_status(PaymentStatus.CONFIRMED)
            return amount
        elif state in ['partially_captured', 'partially_refunded']:
            return amount
        elif state == 'pending':
            payment.change_status(PaymentStatus.WAITING)
        elif state == 'refunded':
            payment.change_status(PaymentStatus.REFUNDED)
            raise PaymentError('Payment already refunded')

    def release(self, payment):
        links = self._get_links(payment)
        url = links['void']['href']
        self._post(payment, url)

    def refund(self, payment, amount=None):
        if amount is None:
            amount = payment.captured_amount
        amount_data = self._get_amount_data(payment, amount)
        refund_data = {'amount': amount_data}
        links = self._get_links(payment)
        url = links['refund']['href']
        self._post(payment, url, data=refund_data)
        payment.change_status(PaymentStatus.REFUNDED)
        return amount
