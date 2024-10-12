from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пользователя."""
        user_count = User.objects.count()

        form_data = {
            'username': 'auth',
            'password1': 'VeryDifficultPassw0rd',
            'password2': 'VeryDifficultPassw0rd',
            'first_name': 'Test',
            'last_name': 'Testov',
            'email': 'example@mail.ru'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(
            User.objects.filter(
                username='auth',
                first_name='Test',
                last_name='Testov',
                email='example@mail.ru'
            ).exists()
        )
