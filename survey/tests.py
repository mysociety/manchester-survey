from django.core.urlresolvers import reverse
from django.test import TestCase

from survey.models import User, Item

class SurveyTest(TestCase):
    def post_survey(self, values):
        self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        if 'permission' not in values:
            values['permission'] = 'Yes'
        self.client.post(reverse('survey:record'), values)

    def get_stored_item(self, key):
        u = User.objects.latest('id')

        responses = Item.objects.filter(user_id=u.id)

        try:
            response = Item.objects.get(user_id=u.id, key=key)
        except Item.DoesNotExist:
            return None
        return response

    def test_front_page_displays(self):
        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

    def test_cannot_complete_survey_twice(self):
        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

        self.client.post(reverse('survey:record'), { 'permission': 'Yes' } )
        self.assertIsNotNone(self.client.cookies['surveydone'])

        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already completed")

    def test_can_override_completion_check(self):
        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

        self.client.post(reverse('survey:record'), { 'permission': 'Yes'} )
        self.assertIsNotNone(self.client.cookies['surveydone'])

        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already completed")

        response = self.client.get(reverse('survey:survey', args=('twfy', 'w')), {'ignorecookie': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already completed")

        # override should only work on staging sites
        with self.settings(DEBUG='1'):
            response = self.client.get(reverse('survey:survey', args=('twfy', 'w')), {'ignorecookie': 1})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "University of Manchester")

    def test_completing_survey_creates_user(self):
        users = User.objects.all()
        count = users.count()

        self.post_survey({})

        users = User.objects.all()
        self.assertEqual(count + 1, users.count())

    def test_survey_is_recorded(self):
        self.post_survey({'1':'a'})

        u = User.objects.latest('id')

        """
        The answer here is 3 as permission is a required field and added by post_survey
        and the view code adds in a recorded field with the datetime
        """
        responses = Item.objects.filter(user_id=u.id)
        self.assertTrue(len(responses) == 3)

        response = Item.objects.filter(user_id=u.id).filter(key='1').filter(value='a')
        self.assertTrue(len(response) == 1)

    def test_multi_value_answers_recorded(self):
        self.post_survey({'1':['b','d']})
        stored = self.get_stored_item('1')
        self.assertEqual('b,d', stored.value)

    def test_email_is_recorded_in_user(self):
        self.post_survey({'1':'a', 'email': 'test@example.org'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual('test@example.org', u.email)

    def test_email_is_blank_if_not_provided(self):
        self.post_survey({'1':'a'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual(u.email, None)
