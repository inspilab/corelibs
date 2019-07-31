from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.conf import settings
from corelibs.middleware.current_user import get_current_authenticated_user
from corelibs.log import Logging
from .constants import (
    LOGGING_HISTORY_MODEL, ACTION_DELETE, ACTION_CREATE, ACTION_UPDATE,
    IGNORE_FIELDS, LANGUAGE_FALLBACK, COUNTRY_FALLBACK, CURRENCY_FALLBACK
)

class Mixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class LogMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def _build_log_data(
            self, actor_type, actor, content_type, content_object_id,
            action_flag, extra_data, message
        ):
        actor_name = ''
        if actor and hasattr(actor, 'first_name') and hasattr(actor, 'last_name'):
            actor_name = "%s %s" % (actor.first_name, actor.last_name)
        elif actor and hasattr(actor, 'first_name'):
            actor_name = "%s" % (actor.first_name)

        return {
            'action_time': datetime.now(),
            'action_date': datetime.now().date(),
            'actor_type': actor_type,
            'actor_id': actor.id if actor and actor.id else '',
            'actor_email': actor.email if actor and hasattr(actor, 'email') and actor.email else '',
            'actor_name': actor_name,
            'actor_photo': actor.photo if actor and hasattr(actor, 'photo') and actor.photo else '',
            'content_type': content_type,
            'content_object_id': content_object_id if content_object_id else '',
            'action_flag': action_flag,
            'extra_data': extra_data,
            'message': message
        }

    def _log_data(self, action_flag, old, new):
        log_data = {}
        extra_data = []
        cls = self.__class__
        user = get_current_authenticated_user()
        actor_type = 'user' if user else 'system'
        if action_flag == ACTION_UPDATE:
            for field in cls._meta.get_fields():
                field_name = field.name
                if field_name in IGNORE_FIELDS:
                    continue

                try:
                    if old and new and getattr(old, field_name) != getattr(new, field_name):
                        extra_data.append(
                            {field_name: str(getattr(new, field_name))}
                        )
                except Exception as e:
                    print(e)

            if len(extra_data) > 0:
                log_data = self._build_log_data(
                    actor_type=actor_type, actor=user, content_type=cls.__name__,
                    content_object_id=new.pk, action_flag=action_flag,
                    extra_data=extra_data, message=''
                )

        elif action_flag == ACTION_DELETE:
            log_data = self._build_log_data(
                actor_type=actor_type, actor=user, content_type=cls.__name__,
                content_object_id=old.pk, action_flag=action_flag,
                extra_data=extra_data, message=''
            )
        elif action_flag == ACTION_CREATE:
            log_data = self._build_log_data(
                actor_type=actor_type, actor=user, content_type=cls.__name__,
                content_object_id=new.pk, action_flag=action_flag,
                extra_data=extra_data, message=''
            )

        logging = Logging()
        logging.send_log(log_data)

    def delete(self, *args, **kwargs):
        old = self.__class__.objects.filter(pk=self.pk).first()
        new = self
        super(LogMixin, self).delete(*args, **kwargs)

        if LOGGING_HISTORY_MODEL:
            self._log_data(action_flag=ACTION_DELETE, old=old, new=new)

    def save(self, *args, **kwargs):
        action_flag = ACTION_UPDATE if self.pk else ACTION_CREATE
        old = self.__class__.objects.filter(pk=self.pk).first()
        new = self
        super(LogMixin, self).save(*args, **kwargs)

        if LOGGING_HISTORY_MODEL:
            self._log_data(action_flag=action_flag, old=old, new=new)


class MultilingualMixin(models.Model):
    language = models.CharField(max_length=10, default=LANGUAGE_FALLBACK)
    country = models.CharField(
        max_length=10, default=COUNTRY_FALLBACK, null=False, blank=True)

    class Meta:
        abstract = True


class MultiCurrenciesMixin(models.Model):
    currency_code = models.CharField(max_length=3, default=CURRENCY_FALLBACK)

    class Meta:
        abstract = True
