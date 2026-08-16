from django.test import TestCase
from django.urls import reverse


class PublicLanguageTests(TestCase):
    def test_russian_browser_uses_english_public_site(self):
        response = self.client.get(
            reverse("planner:feedback"), HTTP_ACCEPT_LANGUAGE="ru-RU,ru;q=0.9"
        )

        self.assertEqual(response.headers["Content-Language"], "en")
        self.assertContains(response, '<html lang="en">', html=False)

    def test_public_language_switcher_rejects_russian(self):
        self.client.post(
            reverse("set_language"),
            {"language": "ru", "next": reverse("planner:feedback")},
        )

        response = self.client.get(reverse("planner:feedback"))
        self.assertEqual(response.headers["Content-Language"], "en")

    def test_login_interface_remains_russian(self):
        response = self.client.get(
            reverse("users:login"), HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9"
        )

        self.assertContains(response, '<html lang="ru">', html=False)
        self.assertContains(response, "Имя пользователя")
