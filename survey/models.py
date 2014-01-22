from django.db import models
from django.utils import timezone

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

    def get_current_week(self):
        startdate = self.startdate
        current = timezone.now()
        diff = current - startdate
        # convert to weeks
        return ( diff.days / 7 ) + 1

    def __unicode__(self):
        return "%s - %s ( %s )" % ( self.code, self.email, self.name )

class Item(models.Model):
    user = models.ForeignKey(User)
    whenstored = models.DateTimeField(auto_now_add=True)
    batch = models.TextField(db_index=True, null=False)
    key = models.TextField(db_index=True, null=False)
    value = models.TextField(db_index=True, null=False)
