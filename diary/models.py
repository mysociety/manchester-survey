from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.template import loader, Context, Template
from django.core.mail import send_mail
from django.contrib import sites

from survey.models import User
from manchester_survey.utils import SurveyDate

class ReminderManager(models.Manager):
    def send_registration_email(self):
        users = User.objects.filter(startdate__isnull=True).exclude(email__isnull=True)

        host = sites.models.Site.objects.get_current()
        template = loader.get_template('email/registration_confirm.txt')

        for user in users:
            context = { 'token': user.generate_token(), 'host': host }
            content = template.render(Context(context))
            send_mail('diary registration', content, 'test@example.org', [user.email])

    def send_first_reminder_email(self):
        sd = SurveyDate()
        today = date.today()
        today = sd.get_start_date(today)
        twelve_weeks_ago = today - timedelta(weeks=12)

        host = sites.models.Site.objects.get_current()
        template = loader.get_template('email/registration_confirm.txt')

        users = User.objects.filter(startdate__gte=twelve_weeks_ago).filter(withdrawn=False)

        for user in users:
            context = { 'token': user.generate_token(), 'host': host }
            content = template.render(Context(context))
            send_mail('this weeks diary', content, 'test@example.org', [user.email])

    def send_second_reminder_email(self):
        sd = SurveyDate()
        today = date.today()
        today = sd.get_start_date(today)

        host = sites.models.Site.objects.get_current()
        template = loader.get_template('email/registration_confirm.txt')

        for week_num in range(0,11):
            start_date = today - timedelta(weeks=week_num)
            end_date = start_date + timedelta(days=4)

            week = Week.objects.get(week=week_num + 1)
            week_id = week.id

            users = User.objects.filter(withdrawn=False).filter(startdate__lte=end_date).filter(startdate__gte=start_date).exclude(entries__week_id=week_id)

            #print 'users for week %d: %d' % ( week_num + 1, users.count() )
            #print 'start: %s, end: %s' % ( start_date, end_date )

            for user in users:
                context = { 'token': user.generate_token(), 'host': host }
                content = template.render(Context(context))
                send_mail('this weeks diary', content, 'test@example.org', [user.email])

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
