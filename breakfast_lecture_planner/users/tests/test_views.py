from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class UsersPagesTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersPagesTestCase.user)

    def test_logout_route_uses_correct_template(self):
        """Роут 'logout' использует соответствующий шаблон."""
        path = reverse('users:logout')
        response = self.authorized_client.get(path)
        self.assertTemplateUsed(response, 'users/logged_out.html')

    def test_login_route_uses_correct_template(self):
        """Роут 'login' использует соответствующий шаблон."""
        path = reverse('users:login')
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_signup_route_uses_correct_template(self):
        """Роут 'signup' использует соответствующий шаблон."""
        path = reverse('users:signup')
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_route_contains_creation_form(self):
        """В контексте страницы 'signup' передается форма
        создания пользователя."""
        path = reverse('users:signup')
        response = self.guest_client.get(path)
        self.assertIsInstance(response.context['form'], CreationForm)

    def test_password_change_route_uses_correct_template(self):
        """Роут 'password_change' использует соответствующий шаблон."""
        path = reverse('users:password_change')
        response = self.authorized_client.get(path)
        self.assertTemplateUsed(response, 'users/password_change_form.html')

    def test_password_change_done_route_uses_correct_template(self):
        """Роут 'password_change_done' использует правильный шаблон."""
        path = reverse('users:password_change_done')
        response = self.authorized_client.get(path)
        self.assertTemplateUsed(response, 'users/password_change_done.html')

    def test_password_reset_route_uses_correct_template(self):
        """Роут 'password_reset' использует соответствующий шаблон."""
        path = reverse('users:password_reset')
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

    def test_password_reset_done_route_uses_correct_template(self):
        """Роут 'password_reset_done' использует соответствующий шаблон."""
        path = reverse('users:password_reset_done')
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/password_reset_done.html')

    def test_password_reset_confirm_route_uses_correct_template(self):
        """Роут 'password_reset_confirm' использует правильный шаблон."""
        path = reverse(
            'users:password_reset_confirm',
            kwargs={'uidb64': 'uid', 'token': 'token'}
        )
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')

    def test_password_reset_complete_route_uses_correct_template(self):
        """Роут 'password_reset_complete' использует соответствующий
        шаблон."""
        path = reverse('users:password_reset_complete')
        response = self.guest_client.get(path)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()
