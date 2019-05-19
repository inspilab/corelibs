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
    def get_price(cls, product_pk=None, variant_pk=None, data=None):
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
