import jwt
from collections import namedtuple

from django.utils.six import text_type
from django.utils.encoding import smart_text
from django.conf import settings as conf_settings
from rest_framework_jwt.settings import api_settings
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication

from .utils import is_match_with_pattern


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
SAFE_URL_PATTERN = ['^\/(.*)'] # This will be set at the main app


class AuthenticationBase(BaseAuthentication):
    """

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

    Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj

    """
    www_authenticate_realm = 'api'

    def authenticate(self, request):
        UserStruct = namedtuple(
            'UserStruct', 'username is_authenticated is_staff is_localguide id pk email first_name last_name'
        )
        jwt_token = self.get_jwt_value(request)
        if not jwt_token:
            return None
        payload = self.valid_request(request, jwt_token)
        if payload and 'username' in payload and 'user_id' in payload:
            user = self.authenticate_credentials(payload, jwt_token)
            if user:
                user_data = UserStruct(
                    username=user['email'],
                    is_authenticated=True,
                    is_staff=user['is_staff'],
                    is_localguide=user['is_localguide'],
                    id=user['id'],
                    pk=user['id'],
                    email=user['email'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                )
                return (user_data, jwt_token)
        else:
            return None

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = ('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = ('Invalid Authorization header. Credentials string \
                should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def valid_request(self, request, token):
        if type(token).__name__ == 'bytes':
            token = token.decode('utf-8')

        payload = None
        is_by_pass = self.is_uri_by_pass_token(request)

        try:
            payload = jwt.decode(token, conf_settings.SECRET_KEY)
        except Exception as e:
            self.raise_exception(
                is_by_pass,
                exceptions.AuthenticationFailed('Invalid token: {}'.format(e))
            )

        return payload

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)

    def raise_exception(self, is_raise, error_obj):
        if is_raise:
            return None
        raise error_obj

    def is_uri_by_pass_token(self, request):
        return (
            request.method in SAFE_METHODS and
            is_match_with_pattern(
                SAFE_URL_PATTERN, request.META.get('PATH_INFO')
            )
        )
