from django.test import TestCase, Client
from django.urls import reverse

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CampusNest')

    def test_about_page_loads(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About CampusNest')

    def test_contact_page_loads(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')

    def test_contact_form_submission(self):
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Inquiry',
            'message': 'Hello CampusNest'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you! Your message has been sent.')
