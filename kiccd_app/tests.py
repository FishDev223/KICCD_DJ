from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Fisher

class LoginViewTests(TestCase):
	def test_invalid_credentials_reopen_the_login_modal(self):
		response = self.client.post(
			reverse('kiccd_app:login'),
			{'username': 'incorrect-user', 'password': 'incorrect-password'},
		)

		self.assertEqual(response.status_code, 400)
		self.assertTemplateUsed(response, 'kiccd_app/index.html')
		self.assertTrue(response.context['login_modal_open'])
		self.assertContains(response, 'Please enter a correct username and password.', status_code=400)
		self.assertContains(response, 'value="incorrect-user"', status_code=400)


class FisherCreatePermissionTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='view-only-user',
			password='test-password',
		)
		self.client.force_login(self.user)

	def test_user_without_add_permission_can_view_disabled_form(self):
		response = self.client.get(reverse('kiccd_app:fisher_create'))

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['can_add_fisher'])
		self.assertContains(response, 'This form is view-only.')
		self.assertContains(response, '<fieldset disabled', html=False)
		self.assertNotContains(response, 'type="submit"')

	def test_user_without_add_permission_cannot_submit_fisher(self):
		response = self.client.post(
			reverse('kiccd_app:fisher_create'),
			{'first_name': 'Ada', 'last_name': 'Lovelace'},
		)

		self.assertEqual(response.status_code, 403)
		self.assertEqual(Fisher.objects.count(), 0)
