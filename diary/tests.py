from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from diary.models import Entries, Week
from survey.models import User

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
