from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from .models import GeneratedWebsite


class AiBuilderTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            password='password123',
        )

    def test_unauthenticated_user_redirected_to_login(self):
        response = self.client.get(reverse('ai_builder:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_dashboard_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('ai_builder:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create a Mini Website AI')

    @patch('ai_builder.views.generate_website_with_gemini')
    def test_dashboard_post_creates_generated_website(self, mock_generate):
        mock_generate.return_value = '<div>Hello {{ user.username }}, this is a mock flight booking site.</div>'
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('ai_builder:dashboard'),
            {'topic': 'Flight Booking'},
        )

        self.assertEqual(GeneratedWebsite.objects.count(), 1)
        generated = GeneratedWebsite.objects.first()
        self.assertEqual(generated.topic, 'Flight Booking')
        self.assertEqual(
            generated.html_content,
            '<div>Hello {{ user.username }}, this is a mock flight booking site.</div>',
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ai_builder:render_website', args=[generated.id]))

    def test_render_website_view_renders_user_username(self):
        self.client.force_login(self.user)
        generated = GeneratedWebsite.objects.create(
            user=self.user,
            topic='Flight Booking',
            html_content='<div>Hello {{ user.username }}, this is a mock flight booking site.</div>',
        )

        response = self.client.get(reverse('ai_builder:render_website', args=[generated.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello admin')
