from django.test import TestCase, Client
from django.urls import reverse
from db_utils import get_db

class ReviewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.db = get_db()
        self.student = self.db.users.find_one({'email': 'student2@demo.com'})
        self.prop = self.db.properties.find_one({'approval_status': 'approved'})

    def test_anonymous_cannot_add_review(self):
        if self.prop:
            prop_id = str(self.prop['_id'])
            response = self.client.post(reverse('reviews:add_review', kwargs={'property_id': prop_id}), {
                'rating': 5,
                'comment': 'Great place to stay during college semesters.'
            })
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('accounts:login'), response.url)

    def test_student_add_review(self):
        if self.student and self.prop:
            session = self.client.session
            session['user_id'] = str(self.student['_id'])
            session['user_role'] = 'student'
            session['user_name'] = self.student['full_name']
            session.save()

            prop_id = str(self.prop['_id'])
            # Clean any previous review for this pair
            self.db.reviews.delete_many({'student_id': str(self.student['_id']), 'property_id': prop_id})

            response = self.client.post(reverse('reviews:add_review', kwargs={'property_id': prop_id}), {
                'rating': 5,
                'comment': 'Very comfortable accommodation with great study environment.'
            })
            self.assertEqual(response.status_code, 302)
