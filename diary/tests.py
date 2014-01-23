from mock import patch, Mock
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils import dateparse, timezone
from django.test import TestCase

from diary.models import Entries, Week
from survey.models import User
from manchester_survey.utils import SurveyDate


class SurveyDateTest(TestCase):
    def test_creation(self):
        sd = SurveyDate('2014-01-23')
        self.assertIsNotNone(sd)

    def test_only_thursday_to_sunday_are_diary_days(self):
        start_date = dateparse.parse_date('2014-01-20')
        sd = SurveyDate(start_date)
        self.assertFalse(sd.is_diary_day())

        for i in range(6):
            date = start_date + timedelta(days=i)
            sd = SurveyDate(date)
            if i < 3:
                self.assertFalse(sd.is_diary_day())
            else:
                self.assertTrue(sd.is_diary_day())

    def test_start_date_gets_nearest_thursday(self):
        today = dateparse.parse_date('2014-01-23')
        self.assertEquals(SurveyDate.get_start_date(today).isoformat(), '2014-01-23')

        today = dateparse.parse_date('2014-01-20')
        self.assertEquals(SurveyDate.get_start_date(today).isoformat(), '2014-01-23')

        today = dateparse.parse_date('2014-01-19')
        self.assertEquals(SurveyDate.get_start_date(today).isoformat(), '2014-01-16')

    def test_get_week_from_startdate(self):
        today = dateparse.parse_date('2014-01-20')

        startdate = dateparse.parse_date('2014-01-23')
        self.assertEquals(SurveyDate.get_week_from_startdate(today, startdate), 0)

        startdate = dateparse.parse_date('2014-01-16')
        self.assertEquals(SurveyDate.get_week_from_startdate(today, startdate), 1)

        startdate = dateparse.parse_date('2014-01-09')
        self.assertEquals(SurveyDate.get_week_from_startdate(today, startdate), 2)


class RegisterPageTest(TestCase):
    def test_registration_page_with_no_token_is_an_error(self):
        response = self.client.get(reverse('diary:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'something went wrong')

    def test_registration_with_token_displays_page(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        response = self.client.get(reverse('diary:register'), {'t': 'token'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'To register and create')

    def test_save_registration_adds_start_date(self):
        u = User(email='test@example.org',token='token',code='usercode')
        u.save()

        # need to do this to set up session
        response = self.client.get(reverse('diary:register'), {'t': 'token'})

        response = self.client.post(reverse('diary:register'), {'name': 'Test User', 'agree': 1})
        self.assertContains(response, 'Thank')

        u = User.objects.get(code='usercode')
        self.assertIsNotNone(u.startdate)
        self.assertEqual(u.name, 'Test User')

class DiaryPageTest(TestCase):
    fixtures = ['initial_data.json']

    def test_questions_page_with_no_token_is_an_error(self):
        response = self.client.get(reverse('diary:questions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Something went wrong finding')

    def test_questions_on_non_diary_day_returns_closed_message(self):
        # see http://www.voidspace.org.uk/python/mock/patch.html#where-to-patch
        # for why it's diary.views and not manchester_survey.utils
        with patch( 'diary.views.SurveyDate') as mock:
            patched_date = mock.return_value
            patched_date.is_diary_day.return_value = False
            response = self.client.get(reverse('diary:questions'))
            self.assertContains(response, 'closed')

    def test_questions_page_displays_correct_week(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        for i in range(11):
            week = i * -1
            startdate = timezone.now() + timedelta(weeks=week)
            u.startdate=startdate
            u.save()
            response = self.client.get(reverse('diary:questions'), {'t': 'token'})
            self.assertContains(response, 'Week %d' % ( i + 1 ))

    def test_startdate_over_12_weeks_ago_is_an_error(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        response = self.client.get(reverse('diary:questions'), {'t': 'token'})
        too_old = timezone.now() + timedelta(weeks=-12)
        u.startdate=too_old
        u.save()
        response = self.client.get(reverse('diary:questions'), {'t': 'token'})
        self.assertContains(response, 'There are no more diary entries')

    def test_diary_details_are_recorded(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        w = Week.objects.get(week=1)

        # do this to set up the session
        response = self.client.get(reverse('diary:questions'), {'t': 'token'})
        response = self.client.post(reverse('diary:record_answers'), { 'media_diary': 'watched the news', 'week': 1 })

        answers = Entries.objects.filter(user_id=u.id).filter(week_id=w.id)
        self.assertEqual(len(answers), 1)
