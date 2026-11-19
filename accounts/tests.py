from django.test import TestCase, Client
from django.urls import reverse
from db_utils import get_db
import uuid

class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.db = get_db()
        self.unique_suffix = uuid.uuid4().hex[:6]
        self.test_email = f"student_{self.unique_suffix}@demo.com"
        self.password = "securepass123"

    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Your Account')

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_registration_validation_fails_on_short_password(self):
        response = self.client.post(reverse('accounts:register'), {
            'full_name': 'Test Student',
            'email': f'shortpass_{self.unique_suffix}@test.com',
            'password': '123',
            'confirm_password': '123',
            'role': 'student',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password must be at least 8 characters')

    def test_user_registration_and_login_flow(self):
        # Register new student
        reg_response = self.client.post(reverse('accounts:register'), {
            'full_name': 'New Student User',
            'email': self.test_email,
            'phone': '9876543210',
            'password': self.password,
            'confirm_password': self.password,
            'role': 'student',
            'college': 'IIT Delhi',
            'city': 'New Delhi',
        })
        self.assertEqual(reg_response.status_code, 302)
        self.assertIn(reverse('accounts:login'), reg_response.url)

        # Login with newly registered user
        login_response = self.client.post(reverse('accounts:login'), {
            'email': self.test_email,
            'password': self.password,
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertIn(reverse('accounts:student_dashboard'), login_response.url)

        # Access dashboard
        dash_response = self.client.get(reverse('accounts:student_dashboard'))
        self.assertEqual(dash_response.status_code, 200)
        self.assertContains(dash_response, 'New Student User')

        # Logout
        logout_response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_response.status_code, 302)

    def test_login_invalid_password(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'student@demo.com',
            'password': 'wrongpassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')
