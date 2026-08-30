from django.test import TestCase
from django.urls import reverse


class StaticPagesTests(TestCase):
    """Simple smoke tests for the informational pages - each one just
    needs to render successfully with a 200 status code, since there's
    no dynamic data or logic involved.
    """

    def test_terms_page_loads(self):
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)

    def test_faq_page_loads(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_loads(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_terms_page_uses_correct_template(self):
        response = self.client.get(reverse('terms'))
        self.assertTemplateUsed(response, 'pages/terms_of_use.html')

    def test_faq_page_uses_correct_template(self):
        response = self.client.get(reverse('faq'))
        self.assertTemplateUsed(response, 'pages/faq.html')

    def test_about_page_uses_correct_template(self):
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'pages/who_are_we.html')