# coding=utf-8

from __future__ import unicode_literals

from tzlocal import get_localzone

from django_app import default_settings, models
from django_app.test import PyW4CTestCase


class DjangoAppTest(PyW4CTestCase):
    def test_default_settings(self):
        # pylint: disable=invalid-name
        APP_NAME = 'django_app'
        DEBUG = True

        settings_dict = dict(default_settings.init_settings(app_name=APP_NAME, debug=DEBUG))

        self.assertEqual(settings_dict['TEMPLATES'][0]['OPTIONS']['debug'], DEBUG)
        self.assertEqual(settings_dict['TIME_ZONE'], get_localzone().zone)
        self.assertIn(APP_NAME, settings_dict['APP_ROOT_DIR'])

    def test_env_to_bool(self):
        self.assertFalse(default_settings.env_to_bool('False'))
        self.assertFalse(default_settings.env_to_bool(0))
        self.assertFalse(default_settings.env_to_bool(''))
        self.assertFalse(default_settings.env_to_bool('FALSE'))
        self.assertFalse(default_settings.env_to_bool('NO'))
        self.assertFalse(default_settings.env_to_bool('JLHSDGLHQSG'))

        self.assertTrue(default_settings.env_to_bool('1'))
        self.assertTrue(default_settings.env_to_bool(1))
        self.assertTrue(default_settings.env_to_bool(42))
        self.assertTrue(default_settings.env_to_bool(-1))
        self.assertTrue(default_settings.env_to_bool('true'))
        self.assertTrue(default_settings.env_to_bool('YES'))

    def test__compute_middleware_settings(self):
        common = 'django.middleware.common.CommonMiddleware'

        self.assertEqual(default_settings._compute_middleware_settings(), (common,))

        self.assertEqual(
            default_settings._compute_middleware_settings(early=('a',), late=('c',)),
            ('a', common, 'c'))

        self.assertEqual(
            default_settings._compute_middleware_settings(early=('a',), late=('c',), use_sentry=True),
            (
                'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
                'a', common, 'c'
            )
        )

    def test_init_web_settings(self):
        app_name = 'django_app'
        web_settings = default_settings.init_web_settings(app_name, False, None)
        self.assertEqual(web_settings['APP_NAME'], app_name)
        self.assertEqual(web_settings['ROOT_URLCONF'], app_name + '.urls')

    def test_context_processors(self):
        web_settings = default_settings.init_web_settings('django_app', False, None, context_processors=('foobar',))
        self.assertIn('foobar', web_settings['TEMPLATES'][0]['OPTIONS']['context_processors'])

    def test_models(self):
        # Check that we can import the models file
        self.assertIn('Work4', models.__doc__)
