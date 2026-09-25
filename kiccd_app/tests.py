from django.test import TestCase
from django.urls import reverse

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
