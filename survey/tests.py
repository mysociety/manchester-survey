import csv, cStringIO

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User as DjangoUser
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
        self.post_survey({'1':'tv'})

        u = User.objects.latest('id')

        """
        The answer here is 3 as permission is a required field and added by post_survey
        and the view code adds in a recorded field with the datetime
        """
        responses = Item.objects.filter(user_id=u.id)
        self.assertTrue(len(responses) == 3)

        response = Item.objects.filter(user_id=u.id).filter(key='1').filter(value='tv')
        self.assertTrue(len(response) == 1)

    def test_multi_value_answers_recorded(self):
        self.post_survey({'1':['tv','newspaper']})
        stored = self.get_stored_item('1')
        self.assertEqual('tv,newspaper', stored.value)

    def test_email_is_recorded_in_user(self):
        self.post_survey({'1':'tv', 'email': 'test@example.org'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual('test@example.org', u.email)

    def test_email_is_blank_if_not_provided(self):
        self.post_survey({'1':'tv'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual(u.email, None)

class ExportBase(TestCase):
    fixtures = ['user_accounts_test_data.json']

    def setUp(self):
        p = Permission.objects.get(codename='can_export')
        u = DjangoUser.objects.get(id=2)
        u.user_permissions.add(p)

    def get_export(self):
        logged_in = self.client.login(username='test2',password='test')
        response = self.client.get(reverse('survey:export'))
        reader = csv.reader(cStringIO.StringIO(response.content))

        return reader


class ExportTest(ExportBase):
    def test_export_requires_login(self):
        response = self.client.get(reverse('survey:export'))
        self.assertEqual(response.status_code, 302)

    def test_export_downloads_csv(self):
        logged_in = self.client.login(username='test2',password='test')
        response = self.client.get(reverse('survey:export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')

    def test_export_has_correct_headers(self):
        logged_in = self.client.login(username='test2',password='test')
        response = self.client.get(reverse('survey:export'))

        all_fields = [
            'id', 'recorded', 'permission', 'tv', 'newspaper', 'internet', 'family', 'other', "1 don't know",
            'a1other', '2', '3', '4', '5', '6', '7government', '7council', '7', '8', '9petition', '9march', '9refused', '9bought',
            '9', '10community', '10country', '10', '11community', '11country', '11', '12community', '12country', '12', '13',
            '14browsed', '14registered', '14joined', '14attended', '14promote', '14other', "14 don't know", '14how',
            '15browsed', '15registered', '15joined', '15attended', '15promote', '15other', "15 don't know", '15how',
            'party_information', 'party_joined', 'party_attended', 'party_voluntary', 'union_information', 'union_joined',
            'union_attended', 'union_voluntary', 'local_information', 'local_joined', 'local_attended', 'local_voluntary',
            'ngo_information', 'ngo_joined', 'ngo_attended', 'ngo_voluntary', 'religious_information', 'religious_joined',
            'religious_attended', 'religious_voluntary', 'hobby_information', 'hobby_joined', 'hobby_attended', 'hobby_voluntary',
            'health_information', 'health_joined', 'health_attended', 'health_voluntary', 'other_information', 'other_joined',
            'other_attended', 'other_voluntary', '16none', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26',
            'blog', 'purchase', 'logged on', 'commented', 'multimedia', 'emailed', 'blog comment', '27 none',
            '28', 'email', 'site', 'source',
        ]

        reader = csv.reader(cStringIO.StringIO(response.content))

        header = reader.next()
        self.assertEqual(header, all_fields)


class ExportMultiChoiceFieldsTest(ExportBase):
    fixtures = ['user_accounts_test_data.json', 'multi_choice_test_data.json']

    def test_question_one(self):
        reader = self.get_export()

        # throw away header
        reader.next()

        answer = [
                '108', '2014-02-10 15:33:03.874897','Yes',"1","","1","","","","","","7","-1","3","","c","","","b","","","","","","c","b","","","","1","a","b","","c","","","","1","","","","","","1","1","","","","","","1","","","","","","1","","","1","1","","","","","1","","","","","","","1","","","","","1","","1","","","","d","b","","33","b","e","","c","Scottish","","","","1","","","","","","","0","twfy","w"
        ]

        row = reader.next()
        self.assertEqual(row, answer)
