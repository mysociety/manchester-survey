import random, hmac, hashlib
from django.conf import settings
from django.db import models

from manchester_survey.utils import base32_to_int, int_to_base32


class UserManager(models.Manager):
    @classmethod
    def get_user_from_token(self, id, token):
        id = base32_to_int(id)
        u = User.objects.get(id=id)
        if u.check_token(token):
            return u

class Sites():
    sites = { 'twfy': 'TheyWorkForYou', 'wtt': 'WriteToThem', 'fms': 'FixMyStreet', 'wtdk': 'WhatDoTheyKnow' }

class Secret(models.Model):
    secret = models.TextField(null=False)

class User(models.Model):
    email = models.TextField(unique=True, null=True, db_index=True)
    name = models.TextField(null=True)
    startdate = models.DateTimeField(null=True)
    withdrawn = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s ( %s )" % ( self.code, self.email, self.name )

    def check_token(self, token):
        try:
            rand, hash = token.split("-")
        except:
            return False

        try:
            rand = base32_to_int(rand)
        except MistypedIDException, e:
            rand = e.args[0]
        except:
            return False

        if self.generate_token(rand) != token:
            return False

        return True

    def generate_token(self, rand):
        rand = int_to_base32(rand)
        hash = hmac.new(settings.SECRET_KEY, unicode(self.id) + rand, hashlib.sha1).hexdigest()[::2]
        return "%s-%s" % (rand, hash)


class Item(models.Model):
    user = models.ForeignKey(User)
    whenstored = models.DateTimeField(auto_now_add=True)
    batch = models.TextField(db_index=True, null=False)
    key = models.TextField(db_index=True, null=False)
    value = models.TextField(db_index=True, null=False)
