from django.test import TestCase
from django.urls import reverse

from .models import User


def make_user(username='testuser', password='testpass'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@test.com')


# ── Model ─────────────────────────────────────────────────────────────────────

class UserModelTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_full_name_with_both_names(self):
        self.user.first_name = 'Jane'
        self.user.last_name = 'Doe'
        self.assertEqual(self.user.full_name, 'Jane Doe')

    def test_full_name_first_name_only(self):
        self.user.first_name = 'Jane'
        self.assertEqual(self.user.full_name, 'Jane')

    def test_full_name_falls_back_to_username(self):
        self.assertEqual(self.user.full_name, 'testuser')

    def test_str_is_username(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_post_count_zero_initially(self):
        self.assertEqual(self.user.post_count, 0)


# ── Auth views ────────────────────────────────────────────────────────────────

class RegisterViewTests(TestCase):
    def test_register_get_ok(self):
        r = self.client.get(reverse('users:register'))
        self.assertEqual(r.status_code, 200)

    def test_register_creates_user_and_logs_in(self):
        r = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(r, reverse('posts:home'))

    def test_register_invalid_password_mismatch(self):
        self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'WrongPass456!',
        })
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_redirects_if_already_authenticated(self):
        make_user()
        self.client.login(username='testuser', password='testpass')
        r = self.client.get(reverse('users:register'))
        self.assertRedirects(r, reverse('posts:home'))


class LoginViewTests(TestCase):
    def setUp(self):
        make_user()

    def test_login_get_ok(self):
        r = self.client.get(reverse('users:login'))
        self.assertEqual(r.status_code, 200)

    def test_login_valid_credentials_redirects_home(self):
        r = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass',
        })
        self.assertRedirects(r, reverse('posts:home'))

    def test_login_invalid_credentials_stays_on_page(self):
        r = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(r.status_code, 200)

    def test_login_respects_next_param(self):
        r = self.client.post(
            reverse('users:login') + '?next=/blog/',
            {'username': 'testuser', 'password': 'testpass'},
        )
        self.assertRedirects(r, '/blog/')

    def test_login_redirects_if_already_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        r = self.client.get(reverse('users:login'))
        self.assertRedirects(r, reverse('posts:home'))


class LogoutViewTests(TestCase):
    def setUp(self):
        make_user()

    def test_logout_redirects_home(self):
        self.client.login(username='testuser', password='testpass')
        r = self.client.get(reverse('users:logout'))
        self.assertRedirects(r, reverse('posts:home'))

    def test_logout_requires_login(self):
        r = self.client.get(reverse('users:logout'))
        self.assertRedirects(r, '/users/login/?next=/users/logout/')


# ── Profile views ─────────────────────────────────────────────────────────────

class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_profile_view_ok(self):
        r = self.client.get(reverse('users:profile', kwargs={'username': 'testuser'}))
        self.assertEqual(r.status_code, 200)

    def test_profile_unknown_user_is_404(self):
        r = self.client.get(reverse('users:profile', kwargs={'username': 'nobody'}))
        self.assertEqual(r.status_code, 404)


class EditProfileViewTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_edit_profile_redirects_anonymous(self):
        r = self.client.get(reverse('users:edit_profile'))
        self.assertRedirects(r, '/users/login/?next=/users/profile/edit/')

    def test_edit_profile_get_ok(self):
        self.client.login(username='testuser', password='testpass')
        r = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(r.status_code, 200)

    def test_edit_profile_updates_fields(self):
        self.client.login(username='testuser', password='testpass')
        self.client.post(reverse('users:edit_profile'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'bio': 'Hello world',
            'website': '',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.bio, 'Hello world')
        self.assertEqual(self.user.email, 'jane@example.com')

    def test_edit_profile_redirects_to_profile_on_success(self):
        self.client.login(username='testuser', password='testpass')
        r = self.client.post(reverse('users:edit_profile'), {
            'first_name': 'Jane',
            'last_name': '',
            'email': 'jane@example.com',
            'bio': '',
            'website': '',
        })
        self.assertRedirects(r, reverse('users:profile', kwargs={'username': 'testuser'}))
