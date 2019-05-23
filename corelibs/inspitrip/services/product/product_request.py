import requests
import json
from requests.exceptions import HTTPError
from .constants import PRODUCT_API_URL


class ProductRequest:
    @classmethod
    def detail_url(cls, product_pk):
        url = "%s/api/products/%s" % (
            PRODUCT_API_URL, product_pk
        )
        return url

    @classmethod
    def get_detail(cls, product_pk):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = cls.detail_url(product_pk)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
