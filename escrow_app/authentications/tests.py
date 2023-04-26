from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from escrow_app import models
class TestAuthentications(APITestCase):
    '''
    A class for testing authentication endpoints
    '''
    def setUp(self) -> None:
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.reset_password = reverse('password_reset_request')
        self.register_data = {
            "email": "yussouffahalu-2656@yopmail.com",
            "phone_number": "08012345678",
            "password": "Password1234"
        }
        self.bad_register_data = {
            "phone_number": "08012345678",
            "password": "Password1234"
        }
        self.login_data = {
            "email": "yussouffahalu-2656@yopmail.com",
            "password": "Password1234"
        }
        self.bad_login_data = {
            "email": "yussouffahalu-2656@yopmail.com"
        }
        return super().setUp()

    def test_create_user_without_email(self):
        with self.assertRaisesMessage(ValueError, "The given email must be set"):
            models.User.objects.create_user(password="123455")
    
    def test_superuser_creation(self):
        user = models.User.objects.create_superuser(email='a@a.com',password='password123')
        self.assertIsInstance(user,models.User)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email,'a@a.com')
    
    def test_create_super_user_with_staff_status(self):
        with self.assertRaisesMessage(ValueError,"Superuser must have is_staff=True."):
            models.User.objects.create_superuser(email='a@a.com',password='password123',is_staff=False)

    def test_create_super_user_with_superuser_status(self):
        with self.assertRaisesMessage(ValueError,"Superuser must have is_superuser=True."):
            models.User.objects.create_superuser(email='a@a.com',password='password123',is_superuser=False)
            
    def test_user_register(self):
        res = self.client.post(self.register_url, self.register_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
    def test_invalid_register(self):
        res = self.client.post(self.register_url, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_register_without_email(self):
        res = self.client.post(self.register_url, self.bad_register_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_login_without_email_verification(self):
        res = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_bad_login(self):
        res = self.client.post(self.login_url, self.bad_login_data, format='json')
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_login_with_verified_email(self):
        res = self.client.post(self.register_url, self.register_data, format='json')
        email = self.register_data['email']
        user = models.User.objects.get(email=email)
        user.is_verified = True
        user.save()
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'tokens')
        self.assertContains(response, 'email')
        
    def test_reset_password(self):
        res = self.client.post(self.reset_password, {"email":"yussouffahalu-2656@yopmail.com"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)