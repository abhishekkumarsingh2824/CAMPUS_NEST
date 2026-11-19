from django.test import TestCase, Client
from django.urls import reverse
from db_utils import get_db

class FavoritesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.db = get_db()
        # Find demo student
        self.student = self.db.users.find_one({'email': 'student@demo.com'})
        # Find demo property
        self.prop = self.db.properties.find_one({'approval_status': 'approved'})

    def test_anonymous_user_redirected_to_login(self):
        if self.prop:
            prop_id = str(self.prop['_id'])
            response = self.client.post(reverse('favorites:toggle', kwargs={'property_id': prop_id}))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('accounts:login'), response.url)

    def test_authenticated_student_can_toggle_favorite(self):
        if self.student and self.prop:
            session = self.client.session
            session['user_id'] = str(self.student['_id'])
            session['user_role'] = 'student'
            session['user_name'] = self.student['full_name']
            session.save()

            prop_id = str(self.prop['_id'])
            response = self.client.post(reverse('favorites:toggle', kwargs={'property_id': prop_id}))
            self.assertEqual(response.status_code, 302)

            # View favorites list
            fav_list_response = self.client.get(reverse('favorites:my_favorites'))
            self.assertEqual(fav_list_response.status_code, 200)
            self.assertContains(fav_list_response, 'Saved Properties')
