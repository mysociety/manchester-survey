import random
import csv, cStringIO

from Cookie import SimpleCookie

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core import mail

from survey.models import User, Item, InvitationManager
from manchester_survey.utils import SurveyDate, int_to_base32

def make_token_args(u):
    id = int_to_base32(u.id)
    token = u.generate_token(random.randint(0,32767))
    return (id, token)

class SurveyTest(TestCase):
    def post_survey(self, values):
        self.client.get(reverse('survey:survey', args=('twfy', 'w')))
        if 'permission' not in values:
            values['permission'] = 'Yes'
        response = self.client.post(reverse('survey:record'), values)
        return response

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
        self.post_survey({'15':'15browsed'})

        u = User.objects.latest('id')

        """
        The answer here is 3 as permission is a required field and added by post_survey
        and the view code adds in a recorded field with the datetime
        """
        responses = Item.objects.filter(user_id=u.id)
        self.assertTrue(len(responses) == 3)

        response = Item.objects.filter(user_id=u.id).filter(key='15').filter(value='15browsed')
        self.assertTrue(len(response) == 1)

    def test_multi_value_answers_recorded(self):
        self.post_survey({'15':['15browsed','15attended']})
        stored = self.get_stored_item('15')
        self.assertEqual('15browsed,15attended', stored.value)

    def test_email_is_recorded_in_user(self):
        self.post_survey({'1':'tv', 'email': 'test@example.org'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual('test@example.org', u.email)

    def test_duplicate_email(self):
        self.post_survey({'1':'tv', 'email': 'test@example.org'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual('test@example.org', u.email)

        self.client.cookies = SimpleCookie()
        response = self.post_survey({'1':'newspaper', 'email': 'test@example.org'})
        self.assertContains(response, 'that email address has already')

    def test_blank_email_submitted_ignores_email(self):
        response = self.post_survey({'1':'tv', 'email': ' '})

        self.assertContains(response, 'Thanks for completing the survey')
        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual(None, u.email)

    def test_invalid_email_display_error(self):
        response = self.post_survey({'1':'tv', 'email': 'invalid'})

        self.assertContains(response, 'Enter a valid email address.')

    def test_email_is_blank_if_not_provided(self):
        self.post_survey({'1':'15browsed'})

        stored = self.get_stored_item('email')
        self.assertIsNone(stored)

        u = User.objects.latest('id')
        self.assertEqual(u.email, None)

class Survey2Test(TestCase):
    def post_survey(self, values):
        u = User(email='test@example.org')
        u.save()
        (rand, hash) = make_token_args(u)

        self.client.get(reverse('survey:survey2', args=(rand, hash)))
        response = self.client.post(reverse('survey:record2'), values)
        return response

    def get_stored_item(self, key):
        u = User.objects.latest('id')

        responses = Item.objects.filter(user_id=u.id)

        try:
            response = Item.objects.get(user_id=u.id, key=key)
        except Item.DoesNotExist:
            return None
        return response

    def test_need_valid_link(self):
        response = self.client.get(reverse('survey:survey2', args=('foo', 'bar')))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'try clicking the link in the email again')


        u = User(email='test@example.org')
        u.save()
        (rand, hash) = make_token_args(u)
        response = self.client.get(reverse('survey:survey2', args=(rand, hash)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'University of Manchester')

    def test_cannot_complete_survey_twice(self):
        u = User(email='test@example.org')
        u.save()
        (rand, hash) = make_token_args(u)

        response = self.client.get(reverse('survey:survey2', args=(rand, hash)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "University of Manchester")

        self.client.post(reverse('survey:record2'), {} )
        self.assertIsNotNone(self.client.cookies['surveydone2'])

        response = self.client.get(reverse('survey:survey2', args=(rand, hash)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already completed")

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
            'id', 'recorded', 'permission', '1', '2', '3', '4', '5', '6', '7', '8government', '8council', '9', '10petition', '10march', '10refused', '10bought',
            '9', '10', '11community', '11country', '11', '12community', '12country', '12', '13community', '13country', '13', '14',
            '15browsed', '15registered', '15joined', '15attended', '15promote', '15other', "15 don't know", '15how',
            '16browsed', '16registered', '16joined', '16attended', '16promote', '16other', "16 don't know", '16how',
            'party_information', 'party_joined', 'party_attended', 'party_voluntary', 'union_information', 'union_joined',
            'union_attended', 'union_voluntary', 'local_information', 'local_joined', 'local_attended', 'local_voluntary',
            'ngo_information', 'ngo_joined', 'ngo_attended', 'ngo_voluntary', 'religious_information', 'religious_joined',
            'religious_attended', 'religious_voluntary', 'hobby_information', 'hobby_joined', 'hobby_attended', 'hobby_voluntary',
            'health_information', 'health_joined', 'health_attended', 'health_voluntary', 'other_information', 'other_joined',
            'other_attended', 'other_voluntary', '17none', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27',
            'blog', 'purchase', 'logged on', 'commented', 'multimedia', 'emailed', 'blog comment', '28 none',
            '29', 'email', 'site', 'source',
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
                '108', '2014-02-10 15:33:03.874897','Yes',"a","","","7","-1","3","","c","","b","","","","","b","","c","b","","","","1","a","b","","c","","","","","","","","","","1","1","","","","","","1","","","","","","1","","","1","1","","","","","1","","","","","","","1","","","","","1","","1","","","","d","b","","33","b","e","","c","Scottish","","","","1","","","","","","","0","twfy","w"
        ]

        row = reader.next()
        self.assertEqual(row, answer)


class SendEmailTest(TestCase):
    fixtures = ['mail_report_test_data.json']

    def test_send_report_email(self):
        im = InvitationManager()
        im.send_diary_feedback_email()

        #import pdb; pdb.set_trace()
        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]

        self.assertEqual(len(sent_mail.to), 1)
        self.assertEqual(sent_mail.to[0], u'one@example.org')

        mail.outbox = []
        im.send_diary_feedback_email()

        self.assertEqual(len(mail.outbox), 0)
