from django.core.urlresolvers import reverse
from django.test import TestCase

from survey.models import User, Item

class StartPageTest(TestCase):
    def post_survey(self, values):
        self.client.get(reverse('survey:survey'))
        self.client.post(reverse('survey:record'), values)

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
        self.post_survey({})
        self.assertIsNotNone(self.client.cookies['usercode'].value)

        usercode = self.client.cookies['usercode']
        u = User.objects.get(code=usercode.value)
        self.assertIsNotNone(u.id)

    def test_survey_is_recorded(self):
        self.post_survey({'1':'a'})

        usercode = self.client.cookies['usercode']
        u = User.objects.get(code=usercode.value)

        responses = Item.objects.filter(user_id=u.id)
        self.assertTrue(len(responses) == 1)

        response = Item.objects.filter(user_id=u.id).filter(key='1').filter(value='a')
        self.assertTrue(len(responses) == 1)
