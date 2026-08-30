from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='StrongPass123!')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_password_is_hashed(self):
        user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.assertNotEqual(user.password, 'StrongPass123!')
        self.assertTrue(user.check_password('StrongPass123!'))


class RegisterViewTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse('users:registration'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post(reverse('users:registration'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('users:login'))

    def test_register_fails_with_mismatched_passwords(self):
        response = self.client.post(reverse('users:registration'), {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!',
        })
        self.assertFalse(User.objects.filter(username='newuser2').exists())

    def test_register_fails_with_duplicate_email(self):
        User.objects.create_user(username='existing', email='taken@example.com', password='StrongPass123!')
        response = self.client.post(reverse('users:registration'), {
            'username': 'anotheruser',
            'email': 'taken@example.com',
            'first_name': 'Alex',
            'last_name': 'Smith',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertFalse(User.objects.filter(username='anotheruser').exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')

    def test_login_page_loads(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_credentials(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'StrongPass123!',
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_password(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'WrongPassword',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileViewTests(TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertNotEqual(response.status_code, 200)

    def test_authenticated_user_sees_profile(self):
        User.objects.create_user(username='testuser', password='StrongPass123!')
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)