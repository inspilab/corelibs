import requests
import json
from requests.exceptions import HTTPError
from .constants import CMS_API_URL


class LocationBreadcrumbRequest:
    @classmethod
    def location_breadcrumb_url(cls, location_code):
        url = "%s/api/location-pages/%s/breadcrumb" % (
            CMS_API_URL, location_code
        )
        return url

    @classmethod
    def get_breadcrumb(cls, location_code):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = cls.location_breadcrumb_url(location_code)
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
        except HTTPError as http_e:
            # Status is NOT 2xx
            raise http_e

        response = res.json()
        return response
