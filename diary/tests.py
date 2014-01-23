from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

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

    def test_questions_page_displays_correct_week(self):
        u = User(email='test@example.org',token='token',code='usercode', startdate=timezone.now())
        u.save()

        response = self.client.get(reverse('diary:questions'), {'t': 'token'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Week 1')
