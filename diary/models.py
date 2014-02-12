import random, sys
from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.template import loader, Context, Template
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import sites
from django.core.management.base import CommandError

from survey.models import User
from manchester_survey.utils import SurveyDate, base32_to_int, int_to_base32

class ReminderManager(models.Manager):
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


    def send_registration_email(self):
        sd = SurveyDate()
        today = sd.now()
        if not settings.DEBUG and today.weekday() != 3:
            raise CommandError("This should only be run on a Thursday")

        users = User.objects.filter(startdate__isnull=True).exclude(email__isnull=True).exclude(reg_email_sent=True)

        self.send_email('email/registration_confirm.txt', 'Participate in the mySociety diary!', settings.FROM_EMAIL, users)

        users.update(reg_email_sent=True)

    """
    Send out an email to tell people that the diary entry is open.
    We send out a different email for people who registered in the preceding Monday-Wednesday
    than those who registered before that. We should not be sending out an email to those
    who registered today as the registration process takes care of that.
    """
    def send_first_reminder_email(self):
        sd = SurveyDate()
        today = sd.now()
        if not settings.DEBUG and today.weekday() != 3:
            raise CommandError("This should only be run on a Thursday")

        today = sd.get_start_date(today)
        twelve_weeks_ago = today - timedelta(weeks=12)

        last_sunday = today - timedelta(days=3)

        users = User.objects.filter(startdate__gte=twelve_weeks_ago).filter(startdate__lte=last_sunday).filter(withdrawn=False)

        self.send_email('email/first_reminder.txt', 'mySociety Diary: your new weekly entry', settings.FROM_EMAIL, users)

        users = User.objects.filter(startdate__gte=last_sunday).filter(startdate__lt=today).filter(withdrawn=False)
        self.send_email('email/late_initial_diary_email.txt', 'mySociety Diary: your first entry', settings.FROM_EMAIL, users)

    def send_second_reminder_email(self):
        sd = SurveyDate()
        today = sd.now()

        if not settings.DEBUG and today.weekday() != 5:
            raise CommandError("This should only be run on a Sunday")

        today = sd.get_start_date(today)

        for week_num in range(0,11):
            start_date = today - timedelta(weeks=week_num)
            end_date = start_date + timedelta(days=4)

            week = Week.objects.get(week=week_num + 1)
            week_id = week.id

            users = User.objects.filter(withdrawn=False).filter(startdate__lte=end_date).filter(startdate__gte=start_date).exclude(entries__week_id=week_id)

            self.send_email('email/second_reminder.txt', 'Don\'t forget to complete your mySociety Diary', settings.FROM_EMAIL, users)

            #print 'users for week %d: %d' % ( week_num + 1, users.count() )
            #print 'start: %s, end: %s' % ( start_date, end_date )

class Week(models.Model):
    week = models.IntegerField()
    template = models.TextField(null=True)

    def __unicode__(self):
        return "%s - %s" % ( self.week, self.template )

class Entries(models.Model):
    user = models.ForeignKey(User)
    week = models.ForeignKey(Week)
    question = models.TextField()
    answer = models.TextField()
