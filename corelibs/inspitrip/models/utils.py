from django.contrib.auth.models import AnonymousUser
from threading import local
from .constants import USER_ATTR_NAME

_thread_locals = local()


def get_current_user():
    current_user = getattr(_thread_locals, USER_ATTR_NAME, None)
    if callable(current_user):
        return current_user()
    return current_user


def get_current_authenticated_user():
    '''
    Return User, Anonymous or None (System)
    '''
    current_user = get_current_user()
    if isinstance(current_user, AnonymousUser):
        return AnonymousUser
    elif current_user:
        return current_user

    return None
