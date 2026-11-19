from django.test import TestCase, Client
from django.urls import reverse
from db_utils import get_db

class InquiriesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.db = get_db()
        self.student = self.db.users.find_one({'email': 'student@demo.com'})
        self.owner = self.db.users.find_one({'email': 'owner@demo.com'})
        self.prop = self.db.properties.find_one({'approval_status': 'approved'})

    def test_anonymous_cannot_send_inquiry(self):
        if self.prop:
            prop_id = str(self.prop['_id'])
            response = self.client.post(reverse('inquiries:send_inquiry', kwargs={'property_id': prop_id}), {
                'message': 'Hello, I am interested in this room for college.'
            })
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('accounts:login'), response.url)

    def test_student_send_inquiry_and_view(self):
        if self.student and self.prop:
            session = self.client.session
            session['user_id'] = str(self.student['_id'])
            session['user_role'] = 'student'
            session['user_name'] = self.student['full_name']
            session.save()

            prop_id = str(self.prop['_id'])
            response = self.client.post(reverse('inquiries:send_inquiry', kwargs={'property_id': prop_id}), {
                'message': 'Hello, I am interested in this room for the academic year.'
            })
            self.assertEqual(response.status_code, 302)

            # View my inquiries
            inq_response = self.client.get(reverse('inquiries:my_inquiries'))
            self.assertEqual(inq_response.status_code, 200)
            self.assertContains(inq_response, 'My Inquiries')

    def test_owner_manage_inquiries(self):
        if self.owner:
            session = self.client.session
            session['user_id'] = str(self.owner['_id'])
            session['user_role'] = 'owner'
            session['user_name'] = self.owner['full_name']
            session.save()

            response = self.client.get(reverse('inquiries:owner_inquiries'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Manage Inquiries')
