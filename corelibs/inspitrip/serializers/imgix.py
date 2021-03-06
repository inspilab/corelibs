from django import template
from django.conf import settings
from rest_framework import serializers
from django_imgix.templatetags.imgix_tags import get_imgix as _get_imgix


def get_imgix(image_url, alias=None, wh=None, **kwargs):
    if image_url.startswith('http://') or image_url.startswith('https://'):
        return image_url
    if hasattr(settings, 'IMGIX_DOMAINS') and settings.IMGIX_DOMAINS and len(settings.IMGIX_DOMAINS) > 0 and settings.IMGIX_DOMAINS[0]:
        if hasattr(settings, 'MEDIAFILES_LOCATION'):
            image_url = '/' + settings.MEDIAFILES_LOCATION + '/' + image_url
        return _get_imgix(image_url=image_url, alias=alias, wh=wh, **kwargs)
    return image_url


class ThumbnailImgixSerializer(serializers.ImageField):

    def __init__(self, alias=None, **kwargs):
        self.alias = alias
        super(ThumbnailImgixSerializer, self).__init__(**kwargs)

    def to_representation(self, instance):
        if instance:
            return get_imgix(image_url=str(instance), alias=self.alias)

        return ''
