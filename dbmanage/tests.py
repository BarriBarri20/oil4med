from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from dbmanage.models import *
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterViewTest(TestCase):
    databases = {'default', 'test'}
    def setUp(self):
        self.client = APIClient()

    def test_register_view(self):
        url = 'http://localhost:8000/register/'


        data = {
            'role': 'farmer',
            'email': 'test2farmer@example.com',
            'password': 'passdwd123',
            'first_name': 'test',
            'last_name': 'regis',
            'country': 'france',
            'address': '7 rue paris',
            'phone_number': '0987654321'
        }
        response = self.client.post(url, data, format='json')

        print("Response Content:", response.content)
        # Verify if the user exists in the test database
        user = Farmer.objects.filter(email='test2farmer@example.com')
        user_exists = User.objects.filter(email='test2farmer@example.com').exists()
        print("User:", user)
        print("userExist:", user_exists)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class LoginViewTest(APITestCase):
    databases = {'default', 'test'}
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(email='test2farmer@example.com',
                                             password='passdwd123',
                                             first_name='First Name',
                                             last_name='Last Name',
                                             role='farmer',)
        self.url = 'http://localhost:8000/login/'

    def test_successful_login(self):
        data = {
            'email': 'test2farmer@example.com',
            'password': 'passdwd123',
        }
        response = self.client.post(self.url, data, format='json')
        print("Response:", response.data)
        self.assertEqual(response.status_code, 200)  # Check if login is successful
        self.assertIn('access', response.data)  # Check if the response contains an access token

    def test_failed_login(self):
        data = {
            'email': 'test2farmer@example.com',
            'password': 'incorrectpassword',
        }
        response = self.client.post(self.url, data, format='json')
        print("Response:", response.data)
        self.assertEqual(response.status_code, 401)  # Check if login failed
        self.assertEqual(response.data, {'detail': 'Invalid credentials'})

class UserAuthenticationTest(APITestCase):
    def setUp(self):
        self.url = '/login/'  # Replace with your actual login API URL
        self.user = User.objects.create_user(email='test@example.com', password='correctpassword')

    def test_successful_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'correctpassword',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)  # Check if login was successful

    def test_login_non_existent_email(self):
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 401)  # Check if login failed

    def test_login_empty_credentials(self):
        data = {
            'email': '',
            'password': '',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 401)  # Check if request was bad

class UserRegistrationTest(APITestCase):
    def setUp(self):
        self.url = '/register/' 
    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)  # Check if registration was successful

    def test_registration_existing_email(self):
        User.objects.create_user(email='existing@example.com', password='existingpassword')
        data = {
            'email': 'existing@example.com',
            'password': 'newpassword',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)  # Check if registration failed

    def test_registration_empty_credentials(self):
        data = {
            'email': '',
            'password': '',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)  # Check if request was bad


class TokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', role='farmer')
        self.refresh_token = RefreshToken.for_user(self.user)

    def test_refresh_token_valid(self):
        url = reverse('refresh-token')  # Replace with your actual refresh token URL
        data = {'refresh': str(self.refresh_token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_invalid(self):
        url = reverse('refresh-token')  # Replace with your actual refresh token URL
        data = {'refresh': 'invalid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
