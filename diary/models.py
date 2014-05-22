import random, sys
from datetime import date, timedelta
from django.db import models
from django.utils import timezone
from django.template import loader, Context, Template
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import sites
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse

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
        twelve_weeks_ago = today - timedelta(weeks=11)

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

            """ special case week 1 as we want to send different mails to people who registered this
                week as they won't have seen the first reminder before so the second one is confusing """
            if week_num == 0:
                self.send_email('email/first_reminder.txt', 'Don\'t forget to complete your mySociety Diary', settings.FROM_EMAIL, users)
            else:
                self.send_email('email/second_reminder.txt', 'Don\'t forget to complete your mySociety Diary', settings.FROM_EMAIL, users)

            #print 'users for week %d: %d' % ( week_num + 1, users.count() )
            #print 'start: %s, end: %s' % ( start_date, end_date )

    def send_email_to_all_diary_participants(self, subject, template):
        sd = SurveyDate()
        today = sd.now()

        today = sd.get_start_date(today)
        twelve_weeks_ago = today - timedelta(weeks=12)

        last_sunday = today - timedelta(days=3)

        users = User.objects.filter(startdate__gte=twelve_weeks_ago).filter(startdate__lte=last_sunday).filter(withdrawn=False)

        self.send_email(template, subject, settings.FROM_EMAIL, users)


    def generate_link(self, user_id):
        user = User.objects.get(pk=int(user_id))
        if user == None:
            print 'No user with that id'
        else:
            id = int_to_base32(user.id)
            token = user.generate_token(random.randint(0,32767))
            url = reverse('diary:questions', args=(id, token,))
            host = sites.models.Site.objects.get_current()
            print 'http://%s%s' % ( host, url )


class ExportManager(models.Manager):
    def export_diary_text(self):
        text_questions = [
            'diary_impact', 'activity_diary', 'news_diary', 'local_diary'
        ]
        entries = Entries.objects.order_by('user_id').order_by('week__week')

        current_user = 0;
        current_week = 0;
        current_file = None;
        for entry in entries:
            if entry.user_id != current_user:
                if current_file:
                    current_file.close()
                file_name = '%s.txt' % entry.user_id
                current_file = open( file_name, 'w' )
                current_file.write( 'user %s' % entry.user_id )
                current_user = entry.user_id

            if current_week != entry.week.week:
                current_file.write( '\n' )
                current_file.write( '=========================\n' )
                current_file.write( '\n' )
                current_file.write( 'week %s\n' % entry.week.week )
                current_file.write( '-----------------------\n' )
                current_file.write( '\n' )
                current_week = entry.week.week

            if entry.question in text_questions:
                current_file.write( entry.question )
                current_file.write( '\n-----------------------\n' )
                current_file.write( entry.answer )
                current_file.write( '\n\n' )




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
