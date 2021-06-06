from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from .models import Person
from rest_framework.authtoken.models import Token
from posts.models import Couriers


# Create your tests here.
class RestFront(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create(username='test_admin', password='test', is_staff=True, is_superuser=True,
                                             is_active=True)
        courier = Couriers.objects.create(**{"courier_id": 1,
                                             "courier_type": 'foot',
                                             "regions": [4, 6, 13],
                                             "working_hours": ['10:20-14:30', '16:00-18:00']
                                             })
        user = User.objects.create(username='username', password='test', email='test@gmail.com',
                                   is_active=True)

        cls.person = Person.objects.create(title='username', age=24, gender='t', phone='+4368786873', courier=courier,
                                           user=user, email='test@gmail.com')

    def test_home_page(self):
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        self.client.force_login(user=self.admin_user)
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_start_page(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_contacts(self):
        response = self.client.post('/contacts', {
            'name': 'chevak',
            'email': 'mail@mail.ru',
            'message': 'Hi!'
        })
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/signup', {
            'email': 'hren'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/signup', {
            'email': 'norm@mail.ru',
            'username': 'username',
            'first_name': 'name',
            'last_name': 'family',
            'phone': '+483958934',
            'password1': 'fhs832467981h73',
            'password2': 'fhs832467981h73',
            'gender': 'm',
            'courier_type': 'bike',
            'regions': '[3, 6]',
            'working_hours': '["14:00-15:00"]',
            'age': '35'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.get('/signup', {
            'email': 'hren',
            'password': 'hren'
        })
        self.assertNotEqual(response.status_code, 302)

        response = self.client.post('/signup', {
            'username': 'test1@gmail.com',
            'password': 'test'
        })
        self.assertNotEqual(response.status_code, 302)

    def test_work(self):
        response = self.client.get('/work')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(user=self.person.user)
        response = self.client.get('/work')
        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        self.client.force_login(user=self.person.user)
        response = self.client.post('/edit', {
            'courier_type': 'hren',
            'regions': '[4, 2, 6]',
            'working_hours': '["10:00-18:00"]'
        })

        self.assertEqual(response.status_code, 200)
        response = self.client.post('/edit', {
            'courier_type': 'foot',
            'regions': '[4, 2, 6]',
            'working_hours': '["10:00-18:00"]'
        })
        self.assertEqual(response.status_code, 200)

    def test_add_order(self):
        response = self.client.post('/add_order', {
            'weight': '12',
            'region': '5',
            'delivery_hours': '["10:00-18:00"]'
        })
        self.assertEqual(response.status_code, 404)

        self.client.force_login(user=self.admin_user)
        response = self.client.post('/add_order', {
            'weight': '9999',
            'region': '5',
            'delivery_hours': '["10:00-18:00"]'
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/add_order', {
            'weight': '12',
            'region': '5',
            'delivery_hours': '["10:00-18:00"]'
        })

        self.assertEqual(response.status_code, 200)
