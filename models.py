from google.appengine.api import mail
from google.appengine.ext import ndb


class SiteConfiguration(ndb.Model):
    target = ndb.StringProperty(indexed=True, required=True)
    name = ndb.StringProperty(indexed=True, required=True)
    check_frequency = ndb.IntegerProperty(indexed=False, required=True)
    enabled = ndb.BooleanProperty(required=True, default=True)
    comment = ndb.TextProperty(indexed=False, required=False)
    monitors = ndb.KeyProperty(repeated=True)


class SiteStatus(object):
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    ERROR = 'ERROR'
    UNEXPECTED = 'UNEXPECTED'

    @staticmethod
    def available(value):
        return value == SiteStatus.ONLINE


class SiteCheck(ndb.Model):
    site = ndb.KeyProperty(kind=SiteConfiguration)
    status = ndb.StringProperty(required=True, choices=[SiteStatus.ONLINE,
                                                        SiteStatus.OFFLINE,
                                                        SiteStatus.ERROR,
                                                        SiteStatus.UNEXPECTED])
    check_time = ndb.DateTimeProperty(auto_now_add=True, indexed=True)


class AlertTarget(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=True)
    enabled = ndb.BooleanProperty(required=True, indexed=True)
    method = ndb.StringProperty(required=True, choices=["EMAIL", "SMS", "BOTH"])  # TODO Enum
    email = ndb.StringProperty(indexed=False, validator=mail.is_email_valid)
    phone = ndb.StringProperty(indexed=False)  # TODO Validator


class AlertSent(ndb.Model):
    failed_check = ndb.KeyProperty(kind=SiteCheck)
    target = ndb.KeyProperty(kind=AlertTarget)
    site = ndb.KeyProperty(kind=SiteConfiguration)