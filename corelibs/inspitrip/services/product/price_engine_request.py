import requests
import json
from requests.exceptions import HTTPError
from .constants import PRODUCT_API_URL


class PriceEngine:
    @classmethod
    def price_url(cls, product_pk, variant_pk):
        url = "%s/api/products/%s/variants/%s/price" % (
            PRODUCT_API_URL, product_pk, variant_pk
        )
        return url

    @classmethod
    def unit_price_url(cls, product_pk, variant_pk, unit_pk, quantity):
        url = "%s/api/products/%s/variants/%s/units/%s/price/%s" % (
            PRODUCT_API_URL, product_pk, variant_pk, unit_pk, quantity
        )
        return url

    @classmethod
    def extra_service_price_url(cls, product_pk, variant_pk, extra_service_pk, quantity):
        url = "%s/api/products/%s/variants/%s/extra-services/%s/price/%s" % (
            PRODUCT_API_URL, product_pk, variant_pk, extra_service_pk, quantity
        )
        return url

    @classmethod
    def get_price(cls, product_pk, variant_pk, data):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        url = cls.price_url(product_pk, variant_pk)
        try:
            res = requests.post(url, data=json.dumps(data), headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response

    @classmethod
    def get_unit_price(cls, product_pk, variant_pk, unit_pk, quantity):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        url = cls.unit_price_url(product_pk, variant_pk, unit_pk, quantity)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response

    @classmethod
    def get_extra_service_price(cls, product_pk, variant_pk, extra_service_pk, quantity):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        url = cls.extra_service_price_url(product_pk, variant_pk, extra_service_pk, quantity)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
