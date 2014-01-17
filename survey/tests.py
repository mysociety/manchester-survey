from django.core.urlresolvers import reverse
from django.test import TestCase

from survey.models import User

class StartPageTest(TestCase):
    def test_front_page_displays(self):
        response = self.client.get(reverse('survey:survey'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

    def test_cannot_complete_survey_twice(self):
        response = self.client.get(reverse('survey:survey'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

        self.client.post(reverse('survey:record'))
        self.assertIsNotNone(self.client.cookies['usercode'])

        response = self.client.get(reverse('survey:survey'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already completed")

    def test_completing_survey_creates_user(self):
        response = self.client.get(reverse('survey:survey'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

        self.client.post(reverse('survey:record'))
        self.assertIsNotNone(self.client.cookies['usercode'].value)

        usercode = self.client.cookies['usercode']
        u = User.objects.get(code=usercode.value)
        self.assertIsNotNone(u.id)
