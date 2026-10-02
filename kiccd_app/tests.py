from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .forms import SampleSiteForm
from .models import Basin, County, Fisher, Pool, Project, SampleSite, SiteType, State, Trib

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


class SampleSiteProjectAssociationTests(TestCase):
	def test_sample_site_form_saves_multiple_projects(self):
		pool = Pool.objects.create(pool_id=1, name='Test Pool')
		basin = Basin.objects.create(name='Test Basin', abbrev='TB')
		state = State.objects.create(state_id=1, name='Test State', abbrev='TS')
		county = County.objects.create(state=state, name='Test County')
		trib = Trib.objects.create(basin=basin, pool=pool, name='Test Tributary')
		site_type = SiteType.objects.create(name='River', abbrev='RIV')
		projects = [
			Project.objects.create(project_id=101, name='Project One'),
			Project.objects.create(project_id=102, name='Project Two'),
		]

		form = SampleSiteForm({
			'name': 'Test Site',
			'type': site_type.pk,
			'pool': pool.pk,
			'state': state.pk,
			'county': county.pk,
			'basin': basin.pk,
			'trib': trib.pk,
			'woody_debris': 'on',
			'submersed_av': 'on',
			'projects': [project.pk for project in projects],
		})

		self.assertTrue(form.is_valid(), form.errors)
		sample_site = form.save()

		self.assertQuerySetEqual(
			sample_site.projects.order_by('project_id'),
			projects,
		)
