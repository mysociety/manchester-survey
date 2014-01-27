from django.db import models


class UserManager(models.Manager):
    @classmethod
    def get_user_from_token(self, token):
        u = User.objects.get(token=token)
        return u

class Sites():
    sites = { 'twfy': 'TheyWorkForYou', 'wtt': 'WriteToThem', 'fms': 'FixMyStreet', 'wtdk': 'WhatDoTheyKnow' }

class Secret(models.Model):
    secret = models.TextField(null=False)

class User(models.Model):
    code = models.TextField(unique=True, null=False, db_index=True)
    email = models.TextField(unique=True, null=True, db_index=True)
    name = models.TextField(null=True)
    startdate = models.DateTimeField(null=True)
    withdrawn = models.BooleanField(default=False)
    token = models.TextField(unique=True, null=True, db_index=True)

    def __unicode__(self):
        return "%s - %s ( %s )" % ( self.code, self.email, self.name )

    def generate_token(self):
        return self.token


class Item(models.Model):
    user = models.ForeignKey(User)
    whenstored = models.DateTimeField(auto_now_add=True)
    batch = models.TextField(db_index=True, null=False)
    key = models.TextField(db_index=True, null=False)
    value = models.TextField(db_index=True, null=False)
