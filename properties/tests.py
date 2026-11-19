from django.test import TestCase, Client
from django.urls import reverse
from db_utils import get_db

class PropertiesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.db = get_db()

    def test_find_rooms_loads(self):
        response = self.client.get(reverse('properties:find_rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find Rooms')

    def test_find_rooms_filter_city(self):
        response = self.client.get(reverse('properties:find_rooms'), {'city': 'Delhi'})
        self.assertEqual(response.status_code, 200)

    def test_find_rooms_search_query(self):
        response = self.client.get(reverse('properties:find_rooms'), {'q': 'Hostel'})
        self.assertEqual(response.status_code, 200)

    def test_property_detail_view(self):
        prop = self.db.properties.find_one({'approval_status': 'approved'})
        if prop:
            prop_id = str(prop['_id'])
            response = self.client.get(reverse('properties:property_detail', kwargs={'property_id': prop_id}))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, prop['title'])

    def test_property_detail_not_found(self):
        response = self.client.get(reverse('properties:property_detail', kwargs={'property_id': '000000000000000000000000'}))
        self.assertEqual(response.status_code, 404)
