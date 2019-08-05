"""Authentication middleware classes.

Userbase Authentication includes classes which solve authenticated issues of the
whole system

"""

import requests
import json
from django.conf import settings as app_settings
from rest_framework import status
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings

from .base import AuthenticationBase


class UserAuthentication(AuthenticationBase):
    """JSON Web Token Authentication middleware class.

    This class extends the token-based authentication class from DRF to encode
    and decore JSON web token.

    This authentication method is about to verify the token to userbase service to make sure
    that users are authenticated & authorized to a particular request.

    """

    def authenticate_credentials(self, payload, jwt_token=None, language=None, country=None):
        """
        Returns an active user from userbase service.
        """
        if not jwt_token:
            msg = ('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        token = jwt_token.decode('utf-8')
        url = app_settings.AUTH_URL
        headers = {
            "Authorization": "%s %s" % (api_settings.JWT_AUTH_HEADER_PREFIX, token)
        }
        if language:
            headers['X-Language'] = language
        if country or country == '':
            headers['X-Country'] = country

        response = requests.get(url, headers=headers)
        if response.status_code == status.HTTP_200_OK and response.text:
            if isinstance(response.text, str):
                response_content = json.loads(response.text)
            if 'user' in response.text:
                return response_content['user']
            msg = ('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)
        msg = ('Invalid signature.')
        raise exceptions.AuthenticationFailed(msg)
