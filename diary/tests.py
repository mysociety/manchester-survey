from django.core.urlresolvers import reverse
from django.test import TestCase

class RegisterPageTest(TestCase):
    def test_register_page_displays(self):
        response = self.client.get(reverse('diary:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "registration page")
