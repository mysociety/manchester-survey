import random, hmac, hashlib
from django.conf import settings
from django.db import models
from django.template import loader, Context, Template
from django.contrib import sites
from django.core.mail import send_mail

from manchester_survey.utils import base32_to_int, int_to_base32


class UserManager(models.Manager):
    @classmethod
    def get_user_from_token(self, id, token):
        id = base32_to_int(id)
        u = User.objects.get(id=id)
        if u.check_token(token):
            return u

class InvitationManager(models.Manager):
    def send_email(self, template, subject, from_address, users):
        host = sites.models.Site.objects.get_current()
        template = loader.get_template(template)

        for user in users:
            if user.email == '':
                continue
            context = {
                    'id': int_to_base32(user.id),
                    'token': user.generate_token(random.randint(0,32767)),
                    'host': host,
                    'contact_email': settings.CONTACT_EMAIL
                    }
            content = template.render(Context(context))
            send_mail(subject, content, from_address, [user.email])

    def send_survey2_invitation_email(self):
        users = User.objects.filter(withdrawn=False).exclude(survey2_email_sent=True).exclude(email__isnull=True)
        self.send_email('email/survey2_invitation.txt', 'mySociety Survey: follow up survey', settings.FROM_EMAIL, users)
        users.update(survey2_email_sent=True)

    def send_survey2_reminder_email(self):
        users = User.objects.filter(withdrawn=False).exclude(survey2_reminder_email_sent=True).exclude(email__isnull=True).exclude(item__batch='2')
        self.send_email('email/survey2_reminder.txt', 'mySociety Survey: follow up survey reminder', settings.FROM_EMAIL, users)
        users.update(survey2_reminder_email_sent=True)

    def send_results_email(self):
        users = User.objects.filter(withdrawn=False).filter(item__batch='2').filter(item__key='26').filter(item__value='report').exclude(results_email_sent=True).exclude(email__isnull=True).distinct('email')
        self.send_email('email/results_published.txt', 'mySociety Survey: results published', settings.FROM_EMAIL, users)
        users.update(results_email_sent=True)

    def send_diary_feedback_email(self):
        users = User.objects.filter(withdrawn=False) \
            .filter(item__batch='2',item__key='26',item__value='report',entries__week_id=12,entries__question='recorded') \
            .exclude(report_email_sent=True) \
            .exclude(email__isnull=True) \
            .distinct('email')
        self.send_email('email/diary_feedback.txt', 'mySociety Survey: asking for diary feedback', settings.FROM_EMAIL, users)
        users.update(report_email_sent=True)

class Sites():
    sites = { 'twfy': 'TheyWorkForYou', 'wtt': 'WriteToThem', 'fms': 'FixMyStreet', 'wtdk': 'WhatDoTheyKnow' }

class Secret(models.Model):
    secret = models.TextField(null=False)

class User(models.Model):
    email = models.TextField(unique=True, null=True, db_index=True)
    name = models.TextField(null=True)
    startdate = models.DateTimeField(null=True)
    withdrawn = models.BooleanField(default=False)
    reg_email_sent = models.BooleanField(default=False)
    survey2_email_sent = models.BooleanField(default=False)
    survey2_reminder_email_sent = models.BooleanField(default=False)
    results_email_sent = models.BooleanField(default=False)
    report_email_sent = models.BooleanField(default=False)

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
