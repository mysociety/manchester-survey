from mock import patch, Mock
from datetime import timedelta, date
from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import dateparse, timezone
from django.test import TestCase

from diary.models import Entries, Week, ReminderManager
from survey.models import User
from manchester_survey.utils import SurveyDate


class SurveyDateTest(TestCase):
    def test_creation(self):
        sd = SurveyDate(date='2014-01-23')
        self.assertIsNotNone(sd)

    def test_only_thursday_to_sunday_are_diary_days(self):
        start_date = dateparse.parse_date('2014-01-20')
        sd = SurveyDate(date=start_date)
        self.assertFalse(sd.is_diary_day())

        for i in range(6):
            date = start_date + timedelta(days=i)
            sd = SurveyDate(date=date)
            if i < 3:
                self.assertFalse(sd.is_diary_day())
            else:
                self.assertTrue(sd.is_diary_day())

    def test_start_date_gets_nearest_thursday(self):
        sd = SurveyDate()
        today = dateparse.parse_date('2014-01-23')
        self.assertEquals(sd.get_start_date(today).isoformat(), '2014-01-23')

        today = dateparse.parse_date('2014-01-20')
        self.assertEquals(sd.get_start_date(today).isoformat(), '2014-01-23')

        today = dateparse.parse_date('2014-01-19')
        self.assertEquals(sd.get_start_date(today).isoformat(), '2014-01-16')

    def test_get_week_from_startdate(self):
        sd = SurveyDate()
        today = dateparse.parse_date('2014-01-20')

        startdate = dateparse.parse_date('2014-01-23')
        self.assertEquals(sd.get_week_from_startdate(today, startdate), 0)

        startdate = dateparse.parse_date('2014-01-16')
        self.assertEquals(sd.get_week_from_startdate(today, startdate), 1)

        startdate = dateparse.parse_date('2014-01-09')
        self.assertEquals(sd.get_week_from_startdate(today, startdate), 2)


class RegistraionEmailTest(TestCase):
    fixtures = ['initial_data.json']

    def run_command(self):
        with patch('diary.models.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_start_date.return_value = dateparse.parse_date('2014-01-23')

            rm = ReminderManager()
            rm.send_registration_email()

    def test_sends_registration_email(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertRegexpMatches(mail.outbox[0].body, 'R/token/')

    def test_does_not_send_if_user_has_startdate(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        startdate='2014-01-16'
        u = User(withdrawn=True,email='test2@example.org',token='token2',code='usercode2', startdate=startdate)
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.org'])

    def test_does_not_send_if_user_has_no_email(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        u = User(withdrawn=True,token='token2',code='usercode2')
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)

class RegisterPageTest(TestCase):
    def test_registration_page_with_no_token_is_an_error(self):
        response = self.client.get(reverse('diary:register', args=('badtoken',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'something went wrong')

    def test_registration_with_token_displays_page(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        response = self.client.get(reverse('diary:register', args=('token',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'To register and create')

    def test_save_registration_adds_start_date(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        # need to do this to set up session
        response = self.client.get(reverse('diary:register', args=('token',)))

        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.now.return_value = dateparse.parse_date('2014-01-24')
            patched_date.get_start_date.return_value = dateparse.parse_datetime('2014-01-23T00:00:00+00:00')

            response = self.client.post(reverse('diary:register', args=('token',)), {'name': 'Test User', 'agree': 1})
            self.assertContains(response, 'Thank')

            u = User.objects.get(code='usercode')
            self.assertIsNotNone(u.startdate)
            self.assertEqual(u.startdate.isoformat(), '2014-01-23T00:00:00+00:00')
            self.assertEqual(u.name, 'Test User')

class DiaryPageTest(TestCase):
    fixtures = ['initial_data.json']

    def test_questions_page_with_bad_token_is_an_error(self):
        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.is_diary_day.return_value = True

            response = self.client.get(reverse('diary:questions', args=('badtoken',)))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Something went wrong finding')

    def test_questions_on_non_diary_day_returns_closed_message(self):
        # see http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
        # for why it's diary.views and not manchester_survey.utils
        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.is_diary_day.return_value = False
            response = self.client.get(reverse('diary:questions', args=('token',)))
            self.assertContains(response, 'closed')

    def test_questions_page_displays_correct_week(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.is_diary_day.return_value = True

            for i in range(1, 12): 
                patched_date.get_week_from_startdate.return_value = i
                response = self.client.get(reverse('diary:questions', args=('token',)))
                self.assertContains(response, 'Week %d' % ( i ))

    def test_startdate_over_12_weeks_ago_is_an_error(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_week_from_startdate.return_value = 13

            response = self.client.get(reverse('diary:questions', args=('token',)))
            response = self.client.get(reverse('diary:questions', args=( 'token',)))
            self.assertContains(response, 'There are no more diary entries')

    def test_diary_details_are_recorded(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        w = Week.objects.get(week=1)

        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_week_from_startdate.return_value = 1

            # do this to set up the session
            response = self.client.get(reverse('diary:questions', args=('token',)))
            response = self.client.post(reverse('diary:record_answers'), { 'media_diary': 'watched the news', 'week': 1 })

            answers = Entries.objects.filter(user_id=u.id).filter(week_id=w.id)
            self.assertEqual(len(answers), 1)

class FirstReminderTest(TestCase):
    fixtures = ['initial_data.json']

    def run_command(self):
        with patch('diary.models.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_start_date.return_value = dateparse.parse_date('2014-01-23')

            rm = ReminderManager()
            rm.send_first_reminder_email()

    def test_sends_reminder(self):
        startdate = '2014-01-23'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertRegexpMatches(mail.outbox[0].body, 'D/token/')

    def test_reminder_not_send_to_withdrawn_users(self):
        startdate = '2014-01-23'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        u = User(withdrawn=True,email='test2@example.org',token='token2',code='usercode2', startdate=startdate)
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.org'])

    def test_reminder_not_sent_to_finished_users(self):
        startdate = '2013-10-31'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        startdate = '2013-10-24'
        u = User(withdrawn=True,email='test2@example.org',token='token2',code='usercode2', startdate=startdate)
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.org'])

    def test_reminder_not_sent_to_not_started_users(self):
        startdate = '2013-10-31'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        startdate = '2014-01-31'
        u = User(withdrawn=True,email='test2@example.org',token='token2',code='usercode2', startdate=startdate)
        u.save()

        self.run_command()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test@example.org'])

class SecondReminderTest(TestCase):
    fixtures = ['initial_data.json']

    def test_sends_reminder(self):
        startdate = '2014-01-23'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        with patch('diary.models.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_start_date.return_value = dateparse.parse_date('2014-01-23')

            rm = ReminderManager()
            rm.send_second_reminder_email()

            self.assertEqual(len(mail.outbox), 1)
            self.assertRegexpMatches(mail.outbox[0].body, 'D/token/')

    def test_no_reminder_sent_before_startdate(self):
        startdate = '2014-01-23'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        with patch('diary.models.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_start_date.return_value = dateparse.parse_date('2014-01-16')

            rm = ReminderManager()
            rm.send_second_reminder_email()

            self.assertEqual(len(mail.outbox), 0)

    def test_no_reminder_sent_if_diary_entry_for_week(self):
        startdate = '2014-01-23'
        u = User(email='test@example.org',token='token',code='usercode', startdate=startdate)
        u.save()

        w = Week.objects.get(week=1)

        e = Entries(user_id=u.id,week_id=w.id,question='q',answer='a')
        e.save()

        with patch('diary.models.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.get_start_date.return_value = dateparse.parse_date('2014-01-23')

            rm = ReminderManager()
            rm.send_second_reminder_email()

            self.assertEqual(len(mail.outbox), 0)
