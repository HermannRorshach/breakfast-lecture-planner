from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='user', password='testpass', email='user@example.com'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(UserUrlTests.user)

    def test_signup_page(self):
        """Страница signup доступна любому пользователю."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_login_page(self):
        """Страница login доступна любому пользователю."""
        response = self.guest_client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_authenticated_user_redirect(self):
        """Авторизованный пользователь перенаправляется на страницу index
        при попытке открыть login."""
        response = self.authorized_client.get(reverse('users:login'))
        self.assertRedirects(response, reverse('posts:index'))

    def test_logout_page_for_authenticated_user(self):
        """Страница logout доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/logged_out.html')

    def test_logout_redirect_for_unauthenticated_user(self):
        """Неавторизованный пользователь со страницы logout перенаправлен
        на страницу login."""
        response = self.guest_client.get(reverse('users:logout'))
        self.assertRedirects(response, reverse('users:login'))

    def test_password_change_form_for_authenticated_user(self):
        """Страница password_change доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('users:password_change'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_change_form.html')

    def test_password_change_done_for_authenticated_user(self):
        """После смены пароля авторизованный пользователь перенаправляется
        на страницу password_change_done."""
        response = self.authorized_client.post(
            reverse('users:password_change'), {
                'old_password': 'testpass',
                'new_password1': 'newpassword123',
                'new_password2': 'newpassword123'
            }
        )
        self.assertRedirects(response, reverse('users:password_change_done'))

    def test_password_reset_form(self):
        """Страница password_reset доступна любому пользователю."""
        response = self.guest_client.get(reverse('users:password_reset'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

    def test_password_reset_email(self):
        """Письмо для сброса пароля отправляется на указанный email
        и перенаправляет на страницу password_reset_done."""
        response = self.guest_client.post(reverse(
            'users:password_reset'), {'email': 'user@example.com'})
        self.assertRedirects(response, reverse('users:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('user@example.com', mail.outbox[0].to)

    def test_password_reset_confirm(self):
        """Переход по ссылке для сброса пароля ведет на соответствующую
        страницу после редиректа."""
        response = self.guest_client.post(
            reverse('users:password_reset'), {'email': 'user@example.com'})
        # Получаем токен и uid из последнего отправленного email
        uid = response.context[0]['uid']
        token = response.context[0]['token']
        # Переходим по URL подтверждения сброса пароля
        response = self.guest_client.get(
            reverse('users:password_reset_confirm', args=[uid, token]))
        # Проверяем, что происходит редирект
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Переходим на страницу, на которую был редирект
        response = self.guest_client.get(response.url)
        # Проверяем, что конечный статус OK
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, что используется правильный шаблон
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')

    def test_password_reset_complete(self):
        """Страница password_reset_complete доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('users:password_reset_complete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')

    def test_password_reset_with_nonexistent_email(self):
        """Не зарегистрированный email не получает письмо для сброса пароля."""
        response = self.guest_client.post(
            reverse('users:password_reset'),
            {'email': 'nonexistent@example.com'})
        self.assertRedirects(response, reverse('users:password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()


'''
    def test_password_reset_link_valid_once_and_complete(self):
        """Ссылка для восстановления пароля действительна только один раз и
        завершает процесс сброса пароля."""
        # Запрос на восстановление пароля
        response = self.guest_client.post(
            reverse('users:password_reset'), {'email': 'user@example.com'})
        self.assertRedirects(response, reverse('users:password_reset_done'))

        # Получаем токен и uid из последнего отправленного email
        email = mail.outbox[0]
        print('email.body =', email.body)
        uid = email.body.split('/')[5]
        print('uid =', uid)
        token = email.body.split('/')[6].split()[0]
        print('token =', token)

        # Первый переход по ссылке и установка нового пароля
        response = self.guest_client.get(
            reverse('users:password_reset_confirm', args=[uid, token]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get(response.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')
        self.assertIn('validlink', response.context)
        self.assertTrue(
            response.context['validlink'],
            "The link should be valid on the first use.")

        # Установка нового пароля
        response = self.guest_client.post(
            reverse('users:password_reset_confirm', args=[uid, token]), {
                'new_password1': 'newpassword123',
                'new_password2': 'newpassword123'
            })
        print('response after post =', response)
        print('response.url after post =', response.url)

        # Переход по установке нового пароля
        response = self.guest_client.get(response.url)
        print('response after get =', response)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Повторный переход по ссылке должен быть неуспешным
        response = self.guest_client.get(
            reverse('users:password_reset_confirm', args=[uid, token]))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get(response.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')
        self.assertIn('validlink', response.context)
        self.assertFalse(response.context.get('validlink'),
        "The link should not be valid after it has been used once.")

        # Проверка, что страница password_reset_complete доступна и использует
        правильный шаблон
        response = self.guest_client.get(
            reverse('users:password_reset_complete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html')
        '''
